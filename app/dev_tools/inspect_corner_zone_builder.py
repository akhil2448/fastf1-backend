from __future__ import annotations

import fastf1

from app.services.race_management.race_analyzer.corner_zone_builder import (
    CornerZoneBuilder,
)

CACHE_DIR = "cache"

YEAR = 2021
ROUND = 14
SESSION = "R"


def main():

    fastf1.Cache.enable_cache(CACHE_DIR)

    session = fastf1.get_session(
        YEAR,
        ROUND,
        SESSION,
    )

    session.load()

    zones = CornerZoneBuilder.build(session)

    print()
    print("=" * 110)
    print("Corner Zones")
    print("=" * 110)
    print()

    for zone in zones:

        corner_names = []

        for corner in zone["corners"]:

            corner_names.append(
                f"{corner['number']}{corner['letter']}"
            )

        print(
            f"Turns {', '.join(corner_names):<18}"
            f" Start {zone['startDistance']:>8.3f} m"
            f" End {zone['endDistance']:>8.3f} m"
            f" Length {(zone['endDistance'] - zone['startDistance']):>7.3f} m"
        )


if __name__ == "__main__":
    main()