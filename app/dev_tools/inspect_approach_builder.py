from __future__ import annotations

import fastf1

from app.services.race_management.race_analyzer.driving_phase_builder import (
    DrivingPhaseBuilder,
)
from app.dev_tools.approach_builder import (
    ApproachBuilder,
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

    circuit_info = session.get_circuit_info()

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

    phases = DrivingPhaseBuilder.build(
        telemetry,
    )

    approaches = ApproachBuilder.build(
        telemetry,
        phases,
        circuit_info,
    )

    print()
    print("=" * 110)
    print("Approach Builder")
    print("=" * 110)
    print()

    for approach in approaches:

        print("-" * 110)

        print(
            f"Phase      : {approach['phase']}"
        )

        print(
            f"Time       : "
            f"{approach['startTime']:.3f}s -> "
            f"{approach['endTime']:.3f}s"
        )

        print(
            f"Distance   : "
            f"{approach['startDistance']:.1f}m -> "
            f"{approach['endDistance']:.1f}m"
        )

        print()

        start = approach["startCorner"]

        print("Start Sample")

        print(
            f"Corner      : "
            f"{start['number']}{start['letter']}"
        )

        print(
            f"Apex Dist   : "
            f"{start['distance']:.2f} m"
        )

        print(
            f"Apex XY     : "
            f"({start['x']:.2f}, "
            f"{start['y']:.2f})"
        )

        print()

        end = approach["endCorner"]

        print("End Sample")

        print(
            f"Corner      : "
            f"{end['number']}{end['letter']}"
        )

        print(
            f"Apex Dist   : "
            f"{end['distance']:.2f} m"
        )

        print(
            f"Apex XY     : "
            f"({end['x']:.2f}, "
            f"{end['y']:.2f})"
        )

        print()

    print("-" * 110)


if __name__ == "__main__":
    main()