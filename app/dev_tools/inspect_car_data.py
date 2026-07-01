import pandas as pd

from app.services.session_cache_service import get_loaded_session

YEAR = 2024
ROUND = 11
DRIVER = "HAM"


def inspect_dataframe(name: str, df: pd.DataFrame):

    print("\n" + "=" * 100)
    print(name)
    print("=" * 100)

    print("\nShape")
    print(df.shape)

    print("\nColumns")
    for c in df.columns:
        print(f"  {c}")

    print("\nIndex Type")
    print(type(df.index))

    print("\nFirst 10 rows")
    print(df.head(10))

    print("\nData Types")
    print(df.dtypes)


def main():

    session = get_loaded_session(
        YEAR,
        ROUND,
    )

    driver_number = (
        session
        .laps
        .pick_drivers(DRIVER)
        .iloc[0]["DriverNumber"]
    )

    driver_number = str(driver_number)

    inspect_dataframe(
        f"Car Data ({DRIVER})",
        session.car_data[driver_number]
    )


if __name__ == "__main__":
    main()