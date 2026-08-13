from __future__ import annotations

import fastf1

from app.services.race_management.race_analyzer.driving_phase_builder import (
    DrivingPhaseBuilder,
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
        telemetry
    )

    print()

    print("=" * 120)
    print("Driving Phases")
    print("=" * 120)

    print()
    
    total_duration = 0.0

    for phase in phases:

        total_duration += phase["duration"]
        print(phase)
    
    print()
    print("=" * 120)
    print("Totals")
    print("=" * 120)
    print()

    lap_time = (
        telemetry.iloc[-1]["Time"].total_seconds()
        - telemetry.iloc[0]["Time"].total_seconds()
    )

    print(f"Lap Time       : {lap_time:.3f} s")
    print(f"Phase Duration : {total_duration:.3f} s")
    print(f"Difference     : {lap_time - total_duration:.6f} s")


if __name__ == "__main__":
    main()