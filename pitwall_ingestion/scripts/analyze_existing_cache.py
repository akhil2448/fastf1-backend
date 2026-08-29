from __future__ import annotations

import sys
from pathlib import Path

# Allow direct execution: python scripts/<name>.py
PROJECT_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PACKAGE_ROOT))

import argparse
from collections import defaultdict

from pitwall_ingestion.validator import filesystem_validate


def fmt(n: int) -> str:
    x = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if x < 1024 or unit == "TB":
            return f"{x:.2f} {unit}"
        x /= 1024
    return f"{x:.2f} TB"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cache", type=Path, nargs="?", default=Path("cache"))
    args = parser.parse_args()

    rows = []
    by_year = defaultdict(lambda: [0, 0, 0])

    for year_dir in sorted(args.cache.iterdir()):
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue
        for event_dir in sorted(year_dir.iterdir()):
            if not event_dir.is_dir():
                continue
            for session_dir in sorted(event_dir.iterdir()):
                if not session_dir.is_dir():
                    continue
                name = session_dir.name.lower()
                if name.endswith("_qualifying"):
                    kind = "Q"
                elif name.endswith("_race"):
                    kind = "R"
                else:
                    continue

                validation = filesystem_validate(session_dir, kind)
                year = int(year_dir.name)
                by_year[year][0] += 1
                by_year[year][1] += validation.size_bytes
                by_year[year][2] += int(validation.complete)
                rows.append((year, event_dir.name, session_dir.name, kind, validation))

    print("Year | Sessions | Complete | Size")
    print("-" * 60)
    for year in sorted(by_year):
        count, size, complete = by_year[year]
        print(f"{year} | {count:8d} | {complete:8d} | {fmt(size)}")

    total = sum(v[1] for v in by_year.values())
    complete = sum(v[2] for v in by_year.values())
    print("-" * 60)
    print(f"TOTAL | {len(rows):8d} | {complete:8d} | {fmt(total)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
