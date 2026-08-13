from __future__ import annotations

import fastf1

from app.services.race_management.race_analyzer.corner_zone_builder import (
    CornerZoneBuilder,
)
from app.services.race_management.race_analyzer.driving_phase_builder import (
    DrivingPhaseBuilder,
)
from app.services.race_management.race_analyzer.zone_progress_builder import (
    ZoneProgressBuilder,
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
        .get_car_data()
        .add_distance()
    )

    phases = DrivingPhaseBuilder.build(
        telemetry,
    )

    corner_zones = CornerZoneBuilder.build(
        session,
    )

    results = ZoneProgressBuilder.build(
        phases,
        corner_zones,
    )

    print()
    print("=" * 110)
    print("Zone Progress")
    print("=" * 110)
    print()

    for result in results:

        zone = result["zone"]

        names = []

        for corner in zone["corners"]:

            names.append(
                f"{corner['number']}{corner['letter']}"
            )

        print("-" * 110)

        print(
            f"Phase          : {result['phase']}"
        )

        print(
            f"Time           : "
            f"{result['startTime']:.3f}s -> "
            f"{result['endTime']:.3f}s"
        )

        print(
            f"Distance       : "
            f"{result['startDistance']:.1f}m -> "
            f"{result['endDistance']:.1f}m"
        )
        
        print(
            f"Phase Length   : "
            f"{result['endDistance'] - result['startDistance']:.1f}m"
        )

        print()

        print(
            f"Corner Zone    : {', '.join(names)}"
        )

        print(
            f"Zone Entry     : "
            f"{zone['startDistance']:.1f}m"
        )

        print(
            f"Zone Exit      : "
            f"{zone['endDistance']:.1f}m"
        )

        print()

        print(
            f"Relationship   : "
            f"{result['relationship']}"
        )

        print(
            f"To Entry       : "
            f"{result['distanceToEntry']:.1f}m"
        )

        print(
            f"To Exit        : "
            f"{result['distanceToExit']:.1f}m"
        )

        print()

        print(
            f"Entry Progress : "
            f"{result['entryProgress']:.1f}%"
        )

        print(
            f"Exit Progress  : "
            f"{result['exitProgress']:.1f}%"
        )


        print()

    print("-" * 110)


if __name__ == "__main__":
    main()