from __future__ import annotations

import fastf1

from app.services.race_management.race_analyzer.driving_phase_builder import (
    DrivingPhaseBuilder,
)
from app.services.race_management.race_analyzer.lift_coast_evidence_builder import (
    LiftCoastEvidenceBuilder,
)

from app.services.race_management.race_analyzer.corner_zone_builder import (
    CornerZoneBuilder,
)

from app.services.race_management.race_analyzer.zone_progress_builder import (
    ZoneProgressBuilder,
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

    corner_zones = CornerZoneBuilder.build(
        session,
    )

    zone_progress = ZoneProgressBuilder.build(
        phases,
        corner_zones,
    )

    result = LiftCoastEvidenceBuilder.build(
        phases,
        telemetry,
        corner_zones,
        zone_progress,
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

            print(
                f"Relationship   : "
                f"{segment['relationship']}"
            )

            print(
                f"Entry Progress : "
                f"{segment['entryProgress']:.1f}%"
            )

            print(
                f"Exit Progress  : "
                f"{segment['exitProgress']:.1f}%"
            )

            print(
                f"To Entry       : "
                f"{segment['distanceToEntry']:.1f}m"
            )

            print(
                f"To Exit        : "
                f"{segment['distanceToExit']:.1f}m"
            )

            print()

            print(
                f"Speed Δ        : "
                f"{segment['speedChange']:.1f} km/h"
            )

            print(
                f"Throttle Δ     : "
                f"{segment['throttleChange']:.0f}%"
            )

            print(
                f"Gear Δ         : "
                f"{segment['gearChange']}"
            )

            print(
                f"RPM Δ          : "
                f"{segment['rpmChange']}"
            )

        print()

    print("-" * 100)


if __name__ == "__main__":
    main()