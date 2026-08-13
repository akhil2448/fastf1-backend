from __future__ import annotations

import fastf1

from app.services.race_management.race_analyzer.driving_phase_builder import (
    DrivingPhaseBuilder,
)
from app.services.race_management.race_analyzer.distribution_builder import (
    DistributionBuilder,
)

from app.services.race_management.race_analyzer.corner_zone_builder import (
    CornerZoneBuilder,
)

from app.services.race_management.race_analyzer.corner_time_builder import (
    CornerTimeBuilder,
)

CACHE_DIR = "cache"

YEAR = 2022
ROUND = 18
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
    
    corner_zones = CornerZoneBuilder.build(
        session,
    )

    phases = DrivingPhaseBuilder.build(
        telemetry,
    )
    
    corner_time = CornerTimeBuilder.build(
        telemetry,
        corner_zones,
    )


    distribution = DistributionBuilder.build(
        phases,
        corner_time,
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
    print("Corner Time")
    print("=" * 80)
    print()

    print(f"Lap Time      : {corner_time['lapTime']:.3f} s")
    print(f"Corner Time   : {corner_time['cornerTime']:.3f} s")
    print(f"Corner Percentage    : {corner_time['cornerPercentage']:.2f}%")

    print()

    print("=" * 80)
    print("Corner Complexes")
    print("=" * 80)
    print()

    for zone in corner_time["zones"]:

        corner_label = ", ".join(
            f"{corner['number']}{corner['letter']}"
            for corner in zone["corners"]
        )

        print(
            f"Turns {corner_label:<18}"
            f"{zone['time']:>7.3f} s"
        )

if __name__ == "__main__":
    main()