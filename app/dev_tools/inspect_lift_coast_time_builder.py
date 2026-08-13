from __future__ import annotations

import fastf1

from app.services.race_management.race_analyzer.driving_phase_builder import (
    DrivingPhaseBuilder,
)
from app.services.race_management.race_analyzer.lift_coast_time_builder import (
    LiftCoastTimeBuilder,
)

from app.services.race_management.race_analyzer.corner_zone_builder import (
    CornerZoneBuilder,
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
    
    corner_zones = CornerZoneBuilder.build(
        session,
    )

    phases = DrivingPhaseBuilder.build(
        telemetry,
    )

    result = LiftCoastTimeBuilder.build(
        phases,
        telemetry,
        corner_zones,
    )

    print()
    print("=" * 100)
    print("Off Throttle")
    print("=" * 100)
    print()

    print(
        f"Lap Time           : {result['lapTime']:.3f} s"
    )
    print(
        f"Off Throttle Time  : {result['offThrottleTime']:.3f} s"
    )
    print(
        f"Percentage         : {result['percentage']:.2f}%"
    )

    print()
    print("=" * 100)
    print("Segments")
    print("=" * 100)
    print()

    for segment in result["segments"]:

        print("-" * 100)

        print(
            f"Phase          : {segment['phase']}"
        )
        print(
            f"Previous Phase : {segment['previousPhase']}"
        )
        print(
            f"Next Phase     : {segment['nextPhase']}"
        )

        print()

        print(
            f"Time           : "
            f"{segment['startTime']:.3f}s -> "
            f"{segment['endTime']:.3f}s"
        )

        print(
            f"Duration       : "
            f"{segment['duration']:.3f}s"
        )

        print()

        print(
            f"Distance       : "
            f"{segment['startDistance']:.1f}m -> "
            f"{segment['endDistance']:.1f}m"
        )

        print()
        
        print(
            f"Speed Start    : {segment['startSpeed']:.1f} km/h"
        )

        print(
            f"Speed Average  : {segment['averageSpeed']:.1f} km/h"
        )

        print(
            f"Speed Minimum  : {segment['minimumSpeed']:.1f} km/h"
        )

        print(
            f"Speed Maximum  : {segment['maximumSpeed']:.1f} km/h"
        )

        print(
            f"Speed End      : {segment['endSpeed']:.1f} km/h"
        )

        print(
            f"Throttle       : "
            f"{segment['startThrottle']:.0f}% -> "
            f"{segment['endThrottle']:.0f}%"
        )

        print(
            f"Brake          : "
            f"{segment['startBrake']} -> "
            f"{segment['endBrake']}"
        )

        print(
            f"Gear           : "
            f"{segment['startGear']} -> "
            f"{segment['endGear']}"
        )

        print(
            f"RPM            : "
            f"{segment['startRPM']} -> "
            f"{segment['endRPM']}"
        )

        print(
            f"DRS            : "
            f"{segment['startDRS']} -> "
            f"{segment['endDRS']}"
        )
        
        print()

        if segment["cornerZone"] is None:

            print("Corner         : None")

        else:

            names = []

            for corner in segment["cornerZone"]["corners"]:

                names.append(
                    f"{corner['number']}{corner['letter']}"
                )

            print(
                f"Corner         : {', '.join(names)}"
            )

            print(
                f"Corner Entry   : "
                f"{segment['cornerZone']['startDistance']:.1f}m"
            )

            print(
                f"Corner Exit    : "
                f"{segment['cornerZone']['endDistance']:.1f}m"
            )

        print()

    print("-" * 100)


if __name__ == "__main__":
    main()