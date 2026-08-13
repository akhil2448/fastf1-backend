from __future__ import annotations

import fastf1

from app.services.race_management.race_analyzer.corner_zone_builder import (
    CornerZoneBuilder,
)
from app.services.race_management.race_analyzer.corner_time_builder import (
    CornerTimeBuilder,
)

CACHE_DIR = "cache"

YEAR = 2023
ROUND = 22
SESSION = "R"
DRIVER = "VER"
LAP = 1


def main():

    fastf1.Cache.enable_cache(CACHE_DIR)

    session = fastf1.get_session(
        YEAR,
        ROUND,
        SESSION,
    )

    session.load()

    lap = (
        session.laps
        .pick_drivers(DRIVER)
        .pick_laps(LAP)
        .iloc[0]
    )

    telemetry = (
        lap
        .get_telemetry()
        .add_distance()
    )

    corner_zones = CornerZoneBuilder.build(session)

    result = CornerTimeBuilder.build(
        telemetry,
        corner_zones,
    )

    print()
    print("=" * 100)
    print("Corner Time")
    print("=" * 100)
    print()

    print(f"Lap Time      : {result['lapTime']:.3f} s")
    print(f"Corner Time   : {result['cornerTime']:.3f} s")
    print(f"Corner Percentage    : {result['cornerPercentage']:.2f}%")

    print()
    print("=" * 100)
    print("Per Corner Complex")
    print("=" * 100)
    print()

    for zone in result["zones"]:

        names = []

        for corner in zone["corners"]:

            names.append(
                f"{corner['number']}{corner['letter']}"
            )

        print(
            f"Turns {', '.join(names):<18}"
            f"{zone['time']:>7.3f} s"
        )


if __name__ == "__main__":
    main()