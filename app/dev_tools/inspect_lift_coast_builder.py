from __future__ import annotations

import fastf1

from app.services.race_management.race_analyzer.corner_zone_builder import (
    CornerZoneBuilder,
)
from app.services.race_management.race_analyzer.driving_phase_builder import (
    DrivingPhaseBuilder,
)
from app.services.race_management.race_analyzer.phase_context_builder import (
    PhaseContextBuilder,
)
from app.services.race_management.race_analyzer.zone_progress_builder import (
    ZoneProgressBuilder,
)
from app.services.race_management.race_analyzer.off_throttle_event_builder import (
    OffThrottleEventBuilder,
)
from app.services.race_management.race_analyzer.lift_coast_builder import (
    LiftCoastBuilder,
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

    #
    # Build pipeline
    #
    corner_zones = CornerZoneBuilder.build(
        session,
    )

    phases = DrivingPhaseBuilder.build(
        telemetry,
    )

    phases = PhaseContextBuilder.build(
        phases,
    )

    zone_progress = ZoneProgressBuilder.build(
        phases,
        corner_zones,
    )

    events = OffThrottleEventBuilder.build(
        phases,
        zone_progress,
    )

    results = LiftCoastBuilder.build(
        events,
    )

    print()
    print("=" * 120)
    print("LIFT & COAST CLASSIFIER")
    print("=" * 120)
    print()

    for index, event in enumerate(results, start=1):

        print("=" * 120)
        print(
            f"EVENT {index}"
        )
        print("=" * 120)
        print()

        print(
            f"Classification : {event['classification']}"
        )

        print(
            f"Score          : {event['score']}"
        )

        print()

        print(
            f"Time           : "
            f"{event['startTime']:.3f}s -> "
            f"{event['endTime']:.3f}s"
        )

        print(
            f"Duration       : "
            f"{event['duration']:.3f}s"
        )

        print()

        print(
            f"Distance       : "
            f"{event['startDistance']:.1f}m -> "
            f"{event['endDistance']:.1f}m"
        )

        print(
            f"Travelled      : "
            f"{event['distance']:.1f}m"
        )

        print()

        print(
            f"Starts With    : {event['startsWith']}"
        )

        print(
            f"Ends With      : {event['endsWith']}"
        )

        print(
            f"Contains Roll  : {event['containsRoll']}"
        )

        print(
            f"Contains Lift  : {event['containsLift']}"
        )

        print()

        print("Reasons")

        for reason in event["reasons"]:

            print(
                f"  • {reason}"
            )

        print()

        print("-" * 120)
        print("PHASES")
        print("-" * 120)
        print()

        for phase in event["phases"]:

            print(
                f"{phase['phase']:5}"
                f" | {phase['relationship']:7}"
                f" | {phase['entryProgress']:5.1f}%"
                f" -> {phase['exitProgress']:5.1f}%"
            )

        print()

    print("=" * 120)


if __name__ == "__main__":
    main()