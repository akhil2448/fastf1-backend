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
from app.services.race_management.race_analyzer.full_throttle_event_builder import (
    FullThrottleEventBuilder,
)
from app.services.race_management.race_analyzer.clipping_builder import (
    ClippingBuilder,
)

CACHE_DIR = "cache"

#
# 2023
# Abu Dhabi = 22
# Monaco    = 6
# Monza     = 14
#
# 2022
# Suzuka    = 18
#

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

    events = FullThrottleEventBuilder.build(
        phases,
        telemetry,
        zone_progress,
    )

    events = ClippingBuilder.build(
        events,
    )

    print()
    print("=" * 120)
    print("CLIPPING PIPELINE")
    print("=" * 120)
    print()

    for index, event in enumerate(events, start=1):

        corners = [
            f"{c['number']}{c['letter']}"
            for c in event["zone"]["corners"]
        ]

        print("-" * 120)

        print(
            f"#{index:02d} "
            f"{event['classification']:16} "
            f"Score={event['score']}  "
            f"Corner={corners}  "
            f"{event['firstRelationship']} -> {event['lastRelationship']}"
        )

        print(
            f"Time={event['startTime']:.3f}-{event['endTime']:.3f}s "
            f"({event['duration']:.3f}s)"
            f" | Dist={event['distance']:.1f}m"
            f" | Entry={event['distanceToEntry']:.1f}m"
        )

        print(
            f"Speed {event['startSpeed']:.0f}"
            f"→{event['endSpeed']:.0f}"
            f" Δ{event['speedGain']:.0f}"
            f" | Avg={event['averageSpeed']:.0f}"
            f" | Max={event['maximumSpeed']:.0f}"
        )

        print(
            f"Accel={event['averageAcceleration']:.1f}"
            f" km/h/s"
        )
        
        print(
            f"Speed Ratio={event['speedRatio']:.3f}"
        )

        print(
            f"Accel Ratio={event['accelerationRatio']:.3f}"
        )

        print(
            f"RPM {event['startRPM']}"
            f"→{event['endRPM']}"
            f" Δ{event['rpmGain']}"
        )

        print(
            f"Gear {event['startGear']}"
            f"→{event['endGear']}"
        )

        print(
            f"DRS {event['startDRS']}"
            f"→{event['endDRS']}"
        )

        print(
            f"Prev Brake={event['previousIsBrake']} "
            f"Next Brake={event['nextIsBrake']}"
        )

        print(
            "Reasons: "
            + (
                ", ".join(event["reasons"])
                if event["reasons"]
                else "None"
            )
        )

        print(
            "Phases : "
            + " | ".join(
                f"{phase['phase']}"
                f"[{phase['relationship']} "
                f"{phase['entryProgress']:.0f}-"
                f"{phase['exitProgress']:.0f}%]"
                for phase in event["phases"]
            )
        )

    print("=" * 120)


if __name__ == "__main__":
    main()