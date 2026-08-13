from __future__ import annotations

import fastf1

from app.services.race_management.race_analyzer.driving_phase_builder import (
    DrivingPhaseBuilder,
)
from app.services.race_management.race_analyzer.distribution_builder import (
    DistributionBuilder,
)

CACHE_DIR = "cache"

YEAR = 2023
ROUND = 22
SESSION = "R"

DRIVER = "VER"
LAP_NUMBER = 1


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

    distribution = DistributionBuilder.build(
        phases,
    )

    print()
    print("=" * 80)
    print("Distribution")
    print("=" * 80)
    print()

    for key, value in distribution.items():

        print(f"{key:<20} {value:>6.2f}%")

    print()

    print("=" * 80)
    print("Corner Phases")
    print("=" * 80)
    print()

    in_corner = False

    for phase in phases:

        if phase["phase"] == "BRAKE":
            in_corner = True

        if in_corner:

            print(
                f"{phase['phase']:<6}"
                f"{phase['startDistance']:>8.1f}m -> "
                f"{phase['endDistance']:>8.1f}m   "
                f"{phase['distance']:>7.1f}m"
            )

        if phase["phase"] == "FULL":
            print()
            in_corner = False


if __name__ == "__main__":
    main()