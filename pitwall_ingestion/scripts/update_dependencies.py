from __future__ import annotations

import sys
from pathlib import Path

# Allow direct execution: python scripts/<name>.py
PROJECT_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PACKAGE_ROOT))

import subprocess

from pitwall_ingestion.version_check import check_versions


def main() -> int:
    versions = check_versions()
    fastf1 = versions["fastf1"]
    print(f"FastF1 installed: {fastf1['installed']}")
    print(f"FastF1 latest:    {fastf1['latest']}")

    if fastf1["update_available"]:
        print("Updating FastF1...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "fastf1"],
            check=True,
        )
        print("FastF1 update complete. Re-run the version check before ingestion.")
    else:
        print("FastF1 is already current or latest version could not be determined.")

    print(
        "Ergast: PitWall uses fastf1.ergast.Ergast; there is no separate Ergast "
        "package to upgrade here."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
