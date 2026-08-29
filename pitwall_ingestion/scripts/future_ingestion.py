from __future__ import annotations

import sys
from pathlib import Path

# Allow direct execution: python scripts/<name>.py
PROJECT_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PACKAGE_ROOT))

import argparse
import json
from dataclasses import replace
from datetime import datetime, timezone, timedelta

from pitwall_ingestion.config import config
from pitwall_ingestion.manifest import Manifest
from pitwall_ingestion.schedule import build_schedule
from pitwall_ingestion.runner import process_sessions
from pitwall_ingestion.sync import sync_session, fetch_remote_manifest, push_manifest


def merge_remote_manifest(local_path: Path) -> None:
    """Seed the local manifest from Oracle so future runs honor server state."""
    if not config.oracle_host:
        return
    raw = fetch_remote_manifest()
    if not raw:
        return

    remote = json.loads(raw)
    local = Manifest(local_path)

    for key, remote_record in remote.get("sessions", {}).items():
        local_record = local.get(key)
        # Prefer COMPLETE server state. For non-complete states the newest
        # local run may contain useful retry details.
        if remote_record.get("status") == "complete":
            local.data["sessions"][key] = remote_record
        elif local_record is None:
            local.data["sessions"][key] = remote_record

    local.save()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch newly completed/current-season Race + Qualifying sessions "
            "and sync verified sessions to Oracle."
        )
    )
    parser.add_argument("--year", type=int, default=config.current_year)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=config.metadata_dir / "future_manifest.json",
    )
    parser.add_argument("--max-sessions", type=int, default=config.max_sessions_per_run)
    parser.add_argument("--no-sync", action="store_true")
    args = parser.parse_args()

    if not args.no_sync:
        merge_remote_manifest(args.manifest)

    now = datetime.now(timezone.utc)
    all_sessions = build_schedule([args.year])

    # A session becomes eligible only after its scheduled session time plus a
    # buffer. This prevents the daily job from hammering a session immediately
    # as it finishes and gives upstream data some time to settle.
    eligible = [
        s for s in all_sessions
        if s.session_date is not None
        and now >= s.session_date + timedelta(
            hours=config.session_completion_buffer_hours
        )
    ]

    print(
        f"Found {len(all_sessions)} Race/Qualifying sessions in {args.year}; "
        f"{len(eligible)} are eligible for acquisition."
    )

    local_config = replace(config, sync_to_oracle=not args.no_sync)
    import pitwall_ingestion.runner as runner
    old_config = runner.config
    runner.config = local_config

    try:
        callback = None if args.no_sync else sync_session
        summary = process_sessions(
            eligible,
            manifest_path=args.manifest,
            sync_callback=callback,
            mode="future",
            max_sessions=args.max_sessions,
        )
    finally:
        runner.config = old_config

    # Publish the updated server-side manifest only after session processing.
    if not args.no_sync and summary["succeeded"]:
        push_manifest(args.manifest)

    print("\n=== FUTURE RUN SUMMARY ===")
    print(f"Processed: {summary['processed']}")
    print(f"Succeeded: {summary['succeeded']}")
    print(f"Skipped:   {summary['skipped']}")
    print(f"Failed:    {summary['failed']}")
    print(f"Stopped:   {summary['stopped']}")
    for failure in summary["failures"]:
        print(f"  - {failure['key']}: {failure['error']}")

    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
