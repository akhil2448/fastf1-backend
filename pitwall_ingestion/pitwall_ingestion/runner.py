from __future__ import annotations

import signal
import time
from pathlib import Path

from .config import config
from .loader import load_complete_candidate
from .manifest import Manifest, SessionRecord, utc_now
from .schedule import PlannedSession
from .validator import filesystem_validate, logical_validate
from .version_check import check_versions
from .notify import notify_run, write_summary

STOP_REQUESTED = False


def _signal_handler(signum, _frame):
    global STOP_REQUESTED
    STOP_REQUESTED = True
    print(
        f"[{utc_now()}] Stop requested (signal {signum}). "
        "No new FastF1 session will be started. The current checkpoint will be preserved.",
        flush=True,
    )


signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


def canonical_session_dir(cache_dir: Path, session) -> Path | None:
    api_path = getattr(session, "api_path", "") or ""
    parts = [p for p in str(api_path).strip("/").split("/") if p]

    # FastF1 API path:
    # /static/YYYY/YYYY-MM-DD_Event/YYYY-MM-DD_Session/
    if len(parts) >= 4 and parts[0] == "static":
        return cache_dir / parts[1] / parts[2] / parts[3]

    return None


def _cooldown_after_session() -> None:
    seconds = max(0.0, float(config.session_cooldown_seconds))
    if seconds <= 0 or STOP_REQUESTED:
        return

    print(
        f"[{utc_now()}] Waiting {seconds:.0f}s before starting the next session...",
        flush=True,
    )

    end = time.monotonic() + seconds
    while not STOP_REQUESTED:
        remaining = end - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(5.0, remaining))


def recover_interrupted_states(manifest: Manifest) -> None:
    """Turn an interrupted fetch into a retryable state."""
    changed = False

    for raw in manifest.data["sessions"].values():
        if raw.get("status") == "fetching":
            raw["status"] = "failed"
            raw["last_error"] = (
                "Previous ingestion run stopped before the session completed. "
                "It will be retried."
            )
            changed = True

    if changed:
        manifest.save()


def ensure_record(manifest: Manifest, planned: PlannedSession) -> dict:
    existing = manifest.get(planned.key)
    if existing:
        return existing

    record = SessionRecord(
        key=planned.key,
        year=planned.year,
        round_number=planned.round_number,
        session_type=planned.session_type,
        event_name=planned.event_name,
        session_date=(planned.session_date.isoformat() if planned.session_date else None),
    )
    manifest.upsert(record)
    manifest.save()
    return manifest.get(planned.key)


def process_sessions(
    planned_sessions: list[PlannedSession],
    *,
    manifest_path: Path,
    sync_callback=None,
    mode: str = "historical",
    max_sessions: int | None = None,
) -> dict:
    """Process scheduled Race/Qualifying sessions sequentially."""
    global STOP_REQUESTED
    STOP_REQUESTED = False

    manifest = Manifest(manifest_path)
    recover_interrupted_states(manifest)

    started_at = utc_now()
    versions = check_versions()

    print(
        f"[{started_at}] FastF1 installed: {versions['fastf1']['installed']}",
        flush=True,
    )

    print(
        f"[{utc_now()}] FastF1 cache: {config.cache_dir}",
        flush=True,
    )

    if versions["fastf1"]["update_available"]:
        print(
            f"[{utc_now()}] NOTICE: newer FastF1 available: "
            f"{versions['fastf1']['latest']} "
            f"(installed {versions['fastf1']['installed']}). "
            "Run update_dependencies.py deliberately; ingestion will not auto-upgrade.",
            flush=True,
        )
        if config.fail_on_newer_fastf1:
            raise RuntimeError("Newer FastF1 version detected; stopping by policy")

    processed = 0
    succeeded = 0
    skipped = 0
    failed = 0
    failures: list[dict] = []
    limit = max_sessions if max_sessions is not None else config.max_sessions_per_run

    for planned in planned_sessions:
        if STOP_REQUESTED or processed >= limit:
            break

        processed += 1
        current = ensure_record(manifest, planned)

        print(
            f"[{utc_now()}] SESSION {planned.key} | {planned.event_name} | "
            f"{planned.session_type}",
            flush=True,
        )

        try:
            # A session that was already successfully archived does not need
            # another FastF1 load. The prior successful run is our checkpoint.
            if current.get("status") == "complete":
                skipped += 1
                print(
                    f"[{utc_now()}] SKIP {planned.key} | already marked complete",
                    flush=True,
                )
                continue

            attempted_at = utc_now()
            manifest.update(
                planned.key,
                status="fetching",
                attempted_at=attempted_at,
                last_error=None,
                retries=int(current.get("retries", 0)) + 1,
                fastf1_version=versions["fastf1"]["installed"],
            )
            manifest.save()

            print(
                f"[{attempted_at}] FETCH {planned.key} | "
                f"{planned.event_name} | {planned.session_type}",
                flush=True,
            )

            session, load_report = load_complete_candidate(planned)

            session_dir = canonical_session_dir(config.cache_dir, session)
            if session_dir is None:
                raise RuntimeError(
                    "FastF1 returned a session but its canonical cache directory "
                    f"could not be resolved for {planned.key}."
                )

            fs = filesystem_validate(session_dir, planned.session_type)
            logical = logical_validate(session, planned.session_type)

            if not fs.complete:
                raise RuntimeError(
                    "Filesystem validation failed: "
                    + ", ".join(fs.missing_files or fs.zero_byte_files or fs.errors)
                )

            if not logical.complete:
                raise RuntimeError(
                    "PitWall session validation failed: "
                    + "; ".join(logical.errors)
                )

            relative_path = str(session_dir.relative_to(config.cache_dir))
            if sync_callback is not None:
                sync_callback(session_dir, relative_path)

            manifest.update(
                planned.key,
                status="complete",
                completed_at=utc_now(),
                size_bytes=fs.size_bytes,
                files=fs.files,
                validation={
                    "filesystem": fs.to_dict(),
                    "logical": logical.to_dict(),
                    "fastf1": load_report.to_dict(),
                    "fastf1_version": versions["fastf1"]["installed"],
                },
            )
            manifest.save()

            succeeded += 1
            fetch_state = "YES" if load_report.had_fetch_activity else "NO"
            print(
                f"[{utc_now()}] SUCCESS {planned.key} | "
                f"{fs.size_bytes:,} bytes | {len(fs.files)} cache files | "
                f"API fetch: {fetch_state}",
                flush=True,
            )

        except Exception as exc:
            failed += 1
            error_text = f"{type(exc).__name__}: {exc}"
            manifest.update(
                planned.key,
                status="failed",
                last_error=error_text,
            )
            manifest.save()
            failures.append({"key": planned.key, "error": error_text})
            print(
                f"[{utc_now()}] FAILED {planned.key} | {error_text}",
                flush=True,
            )

        finally:
            # Deliberate 120-second pause after every session, including
            # successful, skipped, and failed sessions.
            if not STOP_REQUESTED:
                _cooldown_after_session()

    summary = {
        "mode": mode,
        "started_at": started_at,
        "finished_at": utc_now(),
        "processed": processed,
        "succeeded": succeeded,
        "skipped": skipped,
        "failed": failed,
        "stopped": STOP_REQUESTED,
        "failures": failures,
        "fastf1": versions["fastf1"],
    }

    manifest.set_last_run(summary)
    manifest.save()

    summary_path = manifest_path.parent / f"{mode}_last_run.json"
    write_summary(summary, summary_path)
    notify_run(summary, mode)
    return summary
