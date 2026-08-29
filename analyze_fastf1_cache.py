from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import json
import re


CACHE_ROOT = Path("cache")

# Resources that we expect your current PitWall application to need.
# Qualifying deliberately excludes weather/messages for Phase 1.
QUALIFYING_REQUIRED = {
    "session_info.ff1pkl",
    "driver_info.ff1pkl",
    "session_status_data.ff1pkl",
    "track_status_data.ff1pkl",
    "_extended_timing_data.ff1pkl",
    "timing_app_data.ff1pkl",
    "car_data.ff1pkl",
    "position_data.ff1pkl",
}

RACE_REQUIRED = {
    "session_info.ff1pkl",
    "driver_info.ff1pkl",
    "session_status_data.ff1pkl",
    "lap_count.ff1pkl",
    "track_status_data.ff1pkl",
    "_extended_timing_data.ff1pkl",
    "timing_app_data.ff1pkl",
    "car_data.ff1pkl",
    "position_data.ff1pkl",
    "weather_data.ff1pkl",
    "race_control_messages.ff1pkl",
}


def size_bytes(path: Path) -> int:
    total = 0

    if path.is_file():
        return path.stat().st_size

    for p in path.rglob("*"):
        if p.is_file():
            total += p.stat().st_size

    return total


def format_size(n: int) -> str:
    value = float(n)

    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.2f} {unit}"
        value /= 1024

    return f"{value:.2f} TB"


def session_type(session_dir: Path) -> str | None:
    name = session_dir.name.lower()

    if "qualifying" in name:
        return "Qualifying"

    if "race" in name:
        return "Race"

    return None


def analyze_session(session_dir: Path) -> dict:
    session = session_type(session_dir)

    files = {
        p.name: p.stat().st_size
        for p in session_dir.iterdir()
        if p.is_file()
    }

    if session == "Qualifying":
        required = QUALIFYING_REQUIRED
    elif session == "Race":
        required = RACE_REQUIRED
    else:
        required = set()

    present = required & files.keys()
    missing = required - files.keys()

    zero_byte = {
        name for name, size in files.items()
        if size == 0
    }

    # "Likely complete" is deliberately filesystem-based for this first
    # analysis. Later we will validate actual FastF1 properties.
    complete = (
        session in {"Qualifying", "Race"}
        and not missing
        and not zero_byte
    )

    return {
        "session": session,
        "path": str(session_dir),
        "size_bytes": size_bytes(session_dir),
        "files": files,
        "required_present": sorted(present),
        "missing_required": sorted(missing),
        "zero_byte_files": sorted(zero_byte),
        "complete_by_filesystem": complete,
    }


def analyze_cache() -> list[dict]:
    if not CACHE_ROOT.exists():
        raise SystemExit(
            f"Cache directory does not exist: {CACHE_ROOT.resolve()}"
        )

    results = []

    # Expected structure:
    #
    # cache/
    #   2018/
    #     YYYY-MM-DD_Event/
    #       YYYY-MM-DD_Qualifying/
    #       YYYY-MM-DD_Race/
    #
    for year_dir in sorted(CACHE_ROOT.iterdir()):
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue

        year = int(year_dir.name)

        for event_dir in sorted(year_dir.iterdir()):
            if not event_dir.is_dir():
                continue

            for session_dir in sorted(event_dir.iterdir()):
                if not session_dir.is_dir():
                    continue

                kind = session_type(session_dir)

                if kind is None:
                    continue

                result = analyze_session(session_dir)
                result["year"] = year
                result["event"] = event_dir.name
                result["session_dir"] = session_dir.name

                results.append(result)

    return results


def print_report(results: list[dict]) -> None:
    print("\n" + "=" * 110)
    print("FASTF1 CACHE ANALYSIS")
    print("=" * 110)

    total_size = 0
    complete_size = 0
    incomplete_size = 0

    by_year = defaultdict(
        lambda: {
            "sessions": 0,
            "complete": 0,
            "incomplete": 0,
            "size": 0,
        }
    )

    for r in results:
        total_size += r["size_bytes"]

        year_data = by_year[r["year"]]
        year_data["sessions"] += 1
        year_data["size"] += r["size_bytes"]

        if r["complete_by_filesystem"]:
            complete_size += r["size_bytes"]
            year_data["complete"] += 1
            status = "COMPLETE"
        else:
            incomplete_size += r["size_bytes"]
            year_data["incomplete"] += 1
            status = "INCOMPLETE"

        print(
            f"{r['year']} | "
            f"{r['event']} | "
            f"{r['session_dir']} | "
            f"{format_size(r['size_bytes']):>12} | "
            f"{status}"
        )

        if r["missing_required"]:
            print(
                "    Missing:",
                ", ".join(r["missing_required"])
            )

        if r["zero_byte_files"]:
            print(
                "    Zero-byte:",
                ", ".join(r["zero_byte_files"])
            )

    print("\n" + "-" * 110)
    print("YEAR SUMMARY")
    print("-" * 110)

    for year in sorted(by_year):
        d = by_year[year]

        print(
            f"{year}: "
            f"{d['sessions']:3d} sessions | "
            f"{d['complete']:3d} complete | "
            f"{d['incomplete']:3d} incomplete | "
            f"{format_size(d['size'])}"
        )

    print("\n" + "=" * 110)
    print(f"Sessions analyzed : {len(results)}")
    print(f"Complete           : {sum(r['complete_by_filesystem'] for r in results)}")
    print(f"Incomplete         : {sum(not r['complete_by_filesystem'] for r in results)}")
    print(f"Total cache size   : {format_size(total_size)}")
    print(f"Complete size      : {format_size(complete_size)}")
    print(f"Incomplete size    : {format_size(incomplete_size)}")
    print("=" * 110)


def write_json(results: list[dict]) -> None:
    output = Path("fastf1_cache_analysis.json")

    serializable = []

    for r in results:
        serializable.append({
            **r,
            "size": format_size(r["size_bytes"]),
        })

    output.write_text(
        json.dumps(serializable, indent=2),
        encoding="utf-8",
    )

    print(f"\nDetailed report written to: {output.resolve()}")


if __name__ == "__main__":
    results = analyze_cache()
    print_report(results)
    write_json(results)