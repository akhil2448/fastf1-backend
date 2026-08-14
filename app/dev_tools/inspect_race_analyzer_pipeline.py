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

# FOR YEAR 2023, ABU DHABI - 22, MONACO - 6, MONZA - 14
# YEAR 2022, SUZUKA - 18

YEAR = 2023
ROUND = 14
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
        telemetry,
        zone_progress,
    )

    events = LiftCoastBuilder.build(
        events,
    )

    print()
    print("=" * 120)
    print("LIFT & COAST PIPELINE")
    print("=" * 120)
    print()

    for index, event in enumerate(events, start=1):

        print("-" * 120)

        print(
            f"#{index:02} "
            f"{event['classification']:<15} "
            f"Score={event['score']}  "
            f"Corner={event['zone']['corners']}  "
            f"{event['zoneRelationship']}"
        )

        print(
            f"Time={event['startTime']:.3f}-{event['endTime']:.3f}s "
            f"({event['duration']:.3f}s) | "
            f"Dist={event['distance']:.1f}m | "
            f"Entry={event['distanceToEntry']:.1f}m"
        )

        print(
            f"Speed "
            f"{event['startSpeed']:.0f}"
            f"→{event['endSpeed']:.0f} "
            f"Δ{event['speedLoss']:.0f} | "
            f"Avg={event['averageSpeed']:.0f} | "
            f"RPM Δ={event['rpmLoss']} | "
            f"Gear {event['startGear']}→{event['endGear']}"
        )

        print(
            f"Throttle "
            f"{event['startThrottle']:.0f}%"
            f"→{event['endThrottle']:.0f}% "
            f"(Avg {event['averageThrottle']:.1f}%)"
        )

        print(
            f"Prev(T={event['previousIsThrottle']},B={event['previousIsBrake']}) "
            f"Next(T={event['nextIsThrottle']},B={event['nextIsBrake']})"
        )

        print(
            "Reasons: "
            + (
                ", ".join(event["reasons"])
                if event["reasons"]
                else "-"
            )
        )

        phase_summary = " | ".join(
            f"{p['phase']}[{p['relationship']} "
            f"{p['entryProgress']:.0f}-{p['exitProgress']:.0f}%]"
            for p in event["phases"]
        )

        print(f"Phases : {phase_summary}")

    print("=" * 120)


if __name__ == "__main__":
    main()