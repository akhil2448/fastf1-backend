from __future__ import annotations

import fastf1

CACHE_DIR = "cache"

YEAR = 2023
ROUND = 22
SESSION = "R"

DRIVER = "VER"
LAP_NUMBER = 1


def percent(distance, total):
    return round(distance / total * 100, 2)


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
        .copy()
    )

    #
    # Distance travelled between samples.
    #
    telemetry["SegmentDistance"] = (
        telemetry["Distance"]
        .diff()
        .fillna(0)
    )

    total_distance = telemetry["SegmentDistance"].sum()

    full_throttle = telemetry[
        telemetry["Throttle"] == 100
    ]["SegmentDistance"].sum()

    braking = telemetry[
        telemetry["Brake"]
    ]["SegmentDistance"].sum()

    rolling = telemetry[
        (telemetry["Throttle"] == 0)
        & (~telemetry["Brake"])
    ]["SegmentDistance"].sum()

    print()
    print("=" * 80)
    print("Driver Distribution")
    print("=" * 80)

    print(f"Lap distance : {total_distance:.1f} m")
    print()

    print(
        f"Full throttle : {percent(full_throttle, total_distance):6.2f}%"
    )

    print(
        f"Brake         : {percent(braking, total_distance):6.2f}%"
    )

    print(
        f"Rolling       : {percent(rolling, total_distance):6.2f}%"
    )

    print()

    print("=" * 80)
    print("Throttle Values")
    print("=" * 80)

    print(
        telemetry["Throttle"]
        .value_counts()
        .sort_index()
    )

    print()

    print("=" * 80)
    print("Brake Counts")
    print("=" * 80)

    print(
        telemetry["Brake"]
        .value_counts()
    )


if __name__ == "__main__":
    main()