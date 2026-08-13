from __future__ import annotations

import fastf1

CACHE_DIR = "cache"

YEAR = 2023
ROUND = 22
SESSION = "R"

DRIVER = "VER"
LAP_NUMBER = 1


def classify(row):

    throttle = row["Throttle"]
    brake = row["Brake"]

    if brake:
        return "BRAKE"

    if throttle == 100:
        return "FULL"

    if throttle == 0:
        return "ROLL"

    if throttle < 20:
        return "LIFT"

    return "PART"


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

    telemetry["Phase"] = telemetry.apply(
        classify,
        axis=1,
    )

    print()
    print("=" * 120)
    print("Driving Phases")
    print("=" * 120)

    previous = telemetry.iloc[0]

    start_distance = previous["Distance"]
    start_time = previous["Time"]
    phase = previous["Phase"]

    for _, row in telemetry.iloc[1:].iterrows():

        if row["Phase"] != phase:

            print(
                f"{phase:<6}"
                f"  {start_distance:7.1f}m"
                f" -> {row['Distance']:7.1f}m"
                f"   {start_time.total_seconds():7.3f}s"
                f" -> {row['Time'].total_seconds():7.3f}s"
            )

            phase = row["Phase"]
            start_distance = row["Distance"]
            start_time = row["Time"]

    print(
        f"{phase:<6}"
        f"  {start_distance:7.1f}m"
        f" -> {telemetry.iloc[-1]['Distance']:7.1f}m"
        f"   {start_time.total_seconds():7.3f}s"
        f" -> {telemetry.iloc[-1]['Time'].total_seconds():7.3f}s"
    )


if __name__ == "__main__":
    main()