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

# FOR YEAR 2023, ABU DHABI - 22, MONACO - 6, MONZA - 14
# YEAR 2022, SUZUKA - 18

CACHE_DIR = "cache"

YEAR = 2023
ROUND = 6
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

    print()
    print("=" * 110)
    print("OFF THROTTLE EVENTS")
    print("=" * 110)
    print()

    for index, event in enumerate(events, start=1):

        print("=" * 110)
        print(
            f"EVENT {index}"
        )
        print("=" * 110)

        print()

        print(
            f"Start Time      : {event['startTime']:.3f}s"
        )

        print(
            f"End Time        : {event['endTime']:.3f}s"
        )

        print(
            f"Duration        : {event['duration']:.3f}s"
        )

        print()

        print(
            f"Start Distance  : {event['startDistance']:.1f}m"
        )

        print(
            f"End Distance    : {event['endDistance']:.1f}m"
        )

        print(
            f"Distance        : {event['distance']:.1f}m"
        )

        print()

        print(
            f"Phase Count     : {event['phaseCount']}"
        )

        print(
            f"Starts With     : {event['startsWith']}"
        )

        print(
            f"Ends With       : {event['endsWith']}"
        )

        print(
            f"Contains Roll   : {event['containsRoll']}"
        )

        print(
            f"Contains Lift   : {event['containsLift']}"
        )

        print()

        print("-" * 110)
        print("PHASES")
        print("-" * 110)

        print()

        for phase in event["phases"]:


            print(
                f"Phase          : {phase['phase']}"
            )

            print(
                f"Relationship   : {phase['relationship']}"
            )

            print(
                f"Progress       : "
                f"{phase['entryProgress']:.1f}% -> "
                f"{phase['exitProgress']:.1f}%"
            )

            print(
                f"Previous       : {phase['previousPhase']}"
            )

            print(
                f"Next           : {phase['nextPhase']}"
            )
            
            print(
                f"Prev Brake     : {phase['previousIsBrake']}"
            )

            print(
                f"Next Brake     : {phase['nextIsBrake']}"
            )

            print(
                f"Prev Throttle  : {phase['previousIsThrottle']}"
            )

            print(
                f"Next Throttle  : {phase['nextIsThrottle']}"
            )

            print(
                f"To Entry       : {phase['distanceToEntry']:.1f}m"
            )

            print(
                f"To Exit        : {phase['distanceToExit']:.1f}m"
            )

            print()

        print()

    print("=" * 110)


if __name__ == "__main__":
    main()