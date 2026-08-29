from __future__ import annotations

import sys
from pathlib import Path

# Allow direct execution: python scripts/<name>.py
PROJECT_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PACKAGE_ROOT))

import argparse

from pitwall_ingestion.config import config
from pitwall_ingestion.schedule import build_schedule
from pitwall_ingestion.runner import process_sessions


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build the historical 2018+ Race + Qualifying FastF1 archive locally. "
            "Sprint sessions are excluded."
        )
    )
    parser.add_argument("--start-year", type=int, default=config.start_year)
    parser.add_argument("--end-year", type=int, default=config.current_year)
    parser.add_argument(
        "--max-sessions", type=int, default=config.max_sessions_per_run
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=config.metadata_dir / "historical_manifest.json",
    )
    args = parser.parse_args()

    sessions = build_schedule(range(args.start_year, args.end_year + 1))
    print(f"Found {len(sessions)} Race/Qualifying sessions in the schedule.")
    print(
        "Historical mode is local-only. It will not upload to Oracle until the "
        "archive is intentionally transferred."
    )

    summary = process_sessions(
        sessions,
        manifest_path=args.manifest,
        sync_callback=None,
        mode="historical",
        max_sessions=args.max_sessions,
    )

    print("\n=== HISTORICAL RUN SUMMARY ===")
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
