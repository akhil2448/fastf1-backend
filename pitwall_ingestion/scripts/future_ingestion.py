from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Allow direct execution from the repository root or any working directory.
# /repo/pitwall_ingestion/scripts/<name>.py -> repository root is parents[2].
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pitwall_ingestion.config import config
from pitwall_ingestion.manifest import Manifest
from pitwall_ingestion.notify import mac_notification
from pitwall_ingestion.runner import process_sessions
from pitwall_ingestion.schedule import build_schedule, write_merged_schedule_snapshot
from pitwall_ingestion.sync import (
    fetch_remote_manifest,
    push_manifest,
    push_schedule_snapshot,
    sync_session,
)


def merge_remote_manifest(local_path: Path) -> None:
    """Seed local state from Oracle while preserving local retry information."""
    if not config.oracle_host:
        return

    raw = fetch_remote_manifest()
    if not raw:
        return

    remote = json.loads(raw)
    local = Manifest(local_path)

    for key, remote_record in remote.get("sessions", {}).items():
        local_record = local.get(key)

        if remote_record.get("status") == "complete":
            local.data["sessions"][key] = remote_record
        elif local_record is None:
            local.data["sessions"][key] = remote_record

    local.save()


def cleanup_all_remote_complete_local_sessions(manifest_path: Path) -> None:
    """Remove local session directories already marked complete on Oracle."""
    manifest = Manifest(manifest_path)
    for key, record in manifest.data.get("sessions", {}).items():
        if record.get("status") != "complete":
            continue
        relative_path = record.get("cache_path")
        if not relative_path:
            continue
        session_dir = config.cache_dir / relative_path
        try:
            session_dir.relative_to(config.cache_dir)
        except ValueError:
            print(f"[CLEANUP] {key} | refusing unsafe path: {session_dir}", flush=True)
            continue
        if session_dir.exists():
            print(f"[CLEANUP] {key} | removing locally cached session already synced to Oracle", flush=True)
            shutil.rmtree(session_dir)


def cleanup_completed_local_sessions(
    manifest_path: Path,
    completed_keys: list[str],
    planned_by_key: dict[str, object],
) -> None:
    """Delete local temporary session directories after server manifest update."""
    manifest = Manifest(manifest_path)

    for key in completed_keys:
        record = manifest.get(key)
        planned = planned_by_key.get(key)

        if not record or not planned:
            continue

        relative_path = record.get("cache_path")
        if not relative_path:
            print(
                f"[CLEANUP] {key} | no cache_path recorded; leaving local data",
                flush=True,
            )
            continue

        session_dir = config.cache_dir / relative_path

        # Defensive: never remove anything outside the configured FastF1 cache.
        try:
            session_dir.relative_to(config.cache_dir)
        except ValueError:
            print(
                f"[CLEANUP] {key} | refusing unsafe path: {session_dir}",
                flush=True,
            )
            continue

        if not session_dir.exists():
            print(
                f"[CLEANUP] {key} | already absent",
                flush=True,
            )
            continue

        print(
            f"[CLEANUP] {key} | removing local temporary session: {session_dir}",
            flush=True,
        )

        shutil.rmtree(session_dir)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch newly completed Race + Qualifying sessions locally, "
            "validate them, sync them to Oracle, and remove only verified "
            "local session directories."
        )
    )
    parser.add_argument("--year", type=int, default=config.current_year)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=config.metadata_dir / "future_manifest.json",
    )
    parser.add_argument(
        "--schedule-snapshot",
        type=Path,
        default=config.metadata_dir / "schedule_snapshot.json",
    )
    parser.add_argument(
        "--max-sessions",
        type=int,
        default=None,
        help=(
            "Maximum sessions to process in one run. "
            "Default: all currently eligible, pending sessions."
        ),
    )
    parser.add_argument("--no-sync", action="store_true")
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Keep local session directories even after a successful Oracle sync.",
    )
    args = parser.parse_args()

    if args.max_sessions is not None and args.max_sessions < 1:
        raise SystemExit("--max-sessions must be at least 1")

    if not args.no_sync:
        merge_remote_manifest(args.manifest)
        cleanup_all_remote_complete_local_sessions(args.manifest)

    print(
        f"[{datetime.now(timezone.utc).isoformat()}] "
        f"Fetching local FastF1 schedule for {args.year}",
        flush=True,
    )

    try:
        all_sessions = build_schedule([args.year])
    except Exception as exc:
        message = (
            f"Could not load the {args.year} FastF1 schedule locally: "
            f"{type(exc).__name__}: {exc}"
        )
        print(f"[SCHEDULE FAILED] {message}", flush=True)
        mac_notification("PitWall schedule refresh failed", message)
        return 1

    # Save the schedule locally and, when syncing, publish it to Oracle.
    write_merged_schedule_snapshot(args.schedule_snapshot, all_sessions)

    if not args.no_sync:
        push_schedule_snapshot(args.schedule_snapshot)
        print(
            f"[{datetime.now(timezone.utc).isoformat()}] "
            f"Schedule snapshot uploaded to Oracle.",
            flush=True,
        )

    now = datetime.now(timezone.utc)
    eligible = [
        session
        for session in all_sessions
        if (
            session.session_date is not None
            and now
            >= session.session_date
            + timedelta(hours=config.session_completion_buffer_hours)
        )
    ]

    # Do not feed already-complete sessions to the runner. This prevents a
    # future run from spending the 120-second safety cooldown on sessions that
    # are already synced and whose local directories may already be gone.
    manifest = Manifest(args.manifest)
    pending_eligible = [
        session
        for session in eligible
        if manifest.get(session.key) is None
        or manifest.get(session.key).get("status") != "complete"
    ]

    print(
        f"Found {len(all_sessions)} Race/Qualifying sessions in {args.year}; "
        f"{len(eligible)} are eligible after the "
        f"{config.session_completion_buffer_hours:.0f}h safety buffer; "
        f"{len(pending_eligible)} still need ingestion.",
        flush=True,
    )

    local_config = replace(config, sync_to_oracle=not args.no_sync)

    import pitwall_ingestion.runner as runner

    old_config = runner.config
    runner.config = local_config

    try:
        callback = None if args.no_sync else sync_session

        def publish_completed_manifest(_key: str) -> None:
            if not args.no_sync:
                push_manifest(args.manifest)

        summary = process_sessions(
            pending_eligible,
            manifest_path=args.manifest,
            sync_callback=callback,
            post_success_callback=publish_completed_manifest,
            mode="future",
            max_sessions=(
                args.max_sessions
                if args.max_sessions is not None
                else max(1, len(eligible))
            ),
        )
    finally:
        runner.config = old_config

    # Only publish the manifest after all session processing is complete.
    if not args.no_sync:
        push_manifest(args.manifest)

        if summary["completed_keys"] and not args.no_cleanup:
            planned_by_key = {session.key: session for session in pending_eligible}
            cleanup_completed_local_sessions(
                args.manifest,
                summary["completed_keys"],
                planned_by_key,
            )

    print("\n=== FUTURE RUN SUMMARY ===")
    print(f"Processed:        {summary['processed']}")
    print(f"Succeeded:        {summary['succeeded']}")
    print(f"Skipped:          {summary['skipped']}")
    print(f"Failed:           {summary['failed']}")
    print(f"Stopped:          {summary['stopped']}")
    print(f"Completed keys:   {len(summary['completed_keys'])}")

    for failure in summary["failures"]:
        print(f"  - {failure['key']}: {failure['error']}")

    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
