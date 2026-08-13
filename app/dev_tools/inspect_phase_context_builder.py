from __future__ import annotations

import fastf1

from app.services.race_management.race_analyzer.driving_phase_builder import (
    DrivingPhaseBuilder,
)
from app.services.race_management.race_analyzer.phase_context_builder import (
    PhaseContextBuilder,
)

CACHE_DIR = "cache"

# FOR YEAR 2023, ABU DHABI - 22, MONACO - 6, MONZA - 14
# YEAR 2022, SUZUKA - 18

YEAR = 2022
ROUND = 18
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

    phases = PhaseContextBuilder.build(
        phases,
    )

    print()
    print("=" * 110)
    print("Phase Context")
    print("=" * 110)
    print()

    current_event = None

    for index, phase in enumerate(phases):

        #
        # Skip throttle phases.
        #
        if phase["offThrottleEventId"] is None:
            continue

        if current_event != phase["offThrottleEventId"]:

            current_event = phase["offThrottleEventId"]

            print("=" * 110)
            print(
                f"OFF THROTTLE EVENT {current_event}"
            )
            print("=" * 110)
            print()

        print("-" * 110)

        print(
            f"Phase              : {phase['phase']}"
        )

        print()

        print(
            f"Time               : "
            f"{phase['startTime']:.3f}s -> "
            f"{phase['endTime']:.3f}s"
        )

        print(
            f"Duration           : "
            f"{phase['duration']:.3f}s"
        )

        print()

        print(
            f"Distance           : "
            f"{phase['startDistance']:.1f}m -> "
            f"{phase['endDistance']:.1f}m"
        )

        print()

        print(
            f"Previous Phase     : "
            f"{phase['previousPhase']}"
        )

        print(
            f"Next Phase         : "
            f"{phase['nextPhase']}"
        )

        print()

        print(
            f"Previous Brake     : "
            f"{phase['previousIsBrake']}"
        )

        print(
            f"Next Brake         : "
            f"{phase['nextIsBrake']}"
        )

        print()

        print(
            f"Previous Throttle  : "
            f"{phase['previousIsThrottle']}"
        )

        print(
            f"Next Throttle      : "
            f"{phase['nextIsThrottle']}"
        )

        print()

        print(
            f"Previous Duration  : "
            f"{phase['previousDuration']}"
        )

        print(
            f"Next Duration      : "
            f"{phase['nextDuration']}"
        )

        print()

        print(
            f"Previous Distance  : "
            f"{phase['previousDistance']}"
        )

        print(
            f"Next Distance      : "
            f"{phase['nextDistance']}"
        )

        print()

    print("-" * 110)


if __name__ == "__main__":
    main()