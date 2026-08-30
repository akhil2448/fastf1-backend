from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pitwall_ingestion.config import config
from pitwall_ingestion.schedule import build_schedule
from pitwall_ingestion.sync import push_schedule_snapshot


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch an F1 season schedule locally through FastF1 and publish "
            "a schedule snapshot to Oracle."
        )
    )
    parser.add_argument(
        "--year",
        type=int,
        default=config.current_year,
        help="Season year to fetch locally.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=config.metadata_dir / "schedule_snapshot.json",
    )
    parser.add_argument(
        "--no-sync",
        action="store_true",
        help="Write the local snapshot only; do not upload it to Oracle.",
    )
    args = parser.parse_args()

    print(f"Fetching {args.year} season schedule locally through FastF1...")

    try:
        sessions = build_schedule([args.year])
    except Exception as exc:
        print(
            f"SCHEDULE FETCH FAILED: {type(exc).__name__}: {exc}",
            flush=True,
        )
        return 1

    if not sessions:
        print(
            f"SCHEDULE FETCH FAILED: FastF1 returned no Race/Qualifying "
            f"sessions for {args.year}.",
            flush=True,
        )
        return 1

    # Merge with an existing local snapshot so refreshing 2027 does not erase
    # an already-known 2026 schedule.
    from pitwall_ingestion.schedule import merge_schedule_snapshot
    import json

    payload = merge_schedule_snapshot(args.output, sessions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(
        f"Schedule snapshot written: {args.output}",
        flush=True,
    )
    print(
        f"Total Race/Qualifying sessions in snapshot: "
        f"{len(payload['sessions'])}",
        flush=True,
    )

    if not args.no_sync:
        try:
            push_schedule_snapshot(args.output)
        except Exception as exc:
            print(
                f"SCHEDULE UPLOAD FAILED: {type(exc).__name__}: {exc}",
                flush=True,
            )
            return 1

        print("Schedule snapshot uploaded to Oracle.", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
