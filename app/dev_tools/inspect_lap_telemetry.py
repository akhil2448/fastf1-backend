from __future__ import annotations

import fastf1
import pandas as pd

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

    telemetry = lap.get_car_data().add_distance()

    print()
    print("=" * 120)
    print("LAP INFORMATION")
    print("=" * 120)

    print(f"Driver       : {DRIVER}")
    print(f"Lap Number   : {LAP_NUMBER}")
    print(f"Lap Time     : {lap['LapTime']}")
    print(f"Compound     : {lap['Compound']}")
    print(f"Tyre Life    : {lap['TyreLife']}")
    print()

    print("=" * 120)
    print("DATAFRAME INFO")
    print("=" * 120)

    print()

    print(f"Rows    : {len(telemetry)}")
    print(f"Columns : {len(telemetry.columns)}")

    print()

    print("Columns")

    for column in telemetry.columns:
        print(f"  {column}")

    print()

    print("=" * 120)
    print("DTYPES")
    print("=" * 120)

    print()

    print(telemetry.dtypes)

    print()

    print("=" * 120)
    print("HEAD (20)")
    print("=" * 120)

    print()

    print(telemetry.head(20))

    print()

    print("=" * 120)
    print("TAIL (20)")
    print("=" * 120)

    print()

    print(telemetry.tail(20))

    print()

    print("=" * 120)
    print("NUMERIC SUMMARY")
    print("=" * 120)

    print()

    print(
        telemetry.describe(include="all")
    )


if __name__ == "__main__":
    main()