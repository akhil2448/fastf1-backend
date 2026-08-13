from __future__ import annotations

import fastf1

from app.services.race_management.race_analyzer.driving_phase_builder import (
    DrivingPhaseBuilder,
)
from app.services.race_management.race_analyzer.corner_zone_builder import (
    CornerZoneBuilder,
)

# FOR YEAR 2023, ABU DHABI - 22, MONACO - 6, MONZA - 14
# YEAR 2022, SUZUKA - 18

CACHE_DIR = "cache"

YEAR = 2022
ROUND = 18
SESSION = "R"

DRIVER = "VER"
LAP_NUMBER = 1


def find_corner(distance, corner_zones):

    for zone in corner_zones:

        if (
            zone["startDistance"]
            <= distance
            <= zone["endDistance"]
        ):
            return zone

    return None


def format_corner(zone):

    if zone is None:
        return "None"

    names = []

    for corner in zone["corners"]:
        names.append(
            f"{corner['number']}{corner['letter']}"
        )

    return ", ".join(names)


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
        .pick_laps(LAP_NUMBER)
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

    print()
    print("=" * 120)
    print("OFF THROTTLE SEGMENTS")
    print("=" * 120)
    print()

    for index, phase in enumerate(phases):

        #
        # Only inspect OFF throttle phases.
        #
        if phase["phase"] not in (
            "ROLL",
            "LIFT",
        ):
            continue

        previous_phase = (
            phases[index - 1]["phase"]
            if index > 0
            else None
        )

        next_phase = (
            phases[index + 1]["phase"]
            if index < len(phases) - 1
            else None
        )

        corner = find_corner(
            phase["startDistance"],
            corner_zones,
        )

        print("-" * 120)

        print(f"Phase          : {phase['phase']}")
        print(f"Previous Phase : {previous_phase}")
        print(f"Next Phase     : {next_phase}")
        print()

        print(
            f"Time           : "
            f"{phase['startTime']:.3f}s"
            f" -> "
            f"{phase['endTime']:.3f}s"
        )

        print(
            f"Duration       : "
            f"{phase['duration']:.3f}s"
        )

        print()

        print(
            f"Distance       : "
            f"{phase['startDistance']:.1f}m"
            f" -> "
            f"{phase['endDistance']:.1f}m"
        )

        print(
            f"Corner Zone    : "
            f"{format_corner(corner)}"
        )

        if corner:

            print(
                f"Corner Entry   : "
                f"{corner['startDistance']:.1f}m"
            )

            print(
                f"Corner Exit    : "
                f"{corner['endDistance']:.1f}m"
            )

        print()

    print("-" * 120)


if __name__ == "__main__":
    main()