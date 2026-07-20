import pandas as pd

from app.services.session_cache_service import get_loaded_session

YEAR = 2024
ROUND = 11
DRIVER = "HAM"
LAP_NUMBER = 27


def print_value(name, value):

    if isinstance(value, pd.Series):
        print(f"{name:<30}: <Series>")
        return

    if isinstance(value, pd.DataFrame):
        print(f"{name:<30}: <DataFrame>")
        return

    print(f"{name:<30}: {value}")


def main():

    session = get_loaded_session(
        YEAR,
        ROUND,
    )

    lap = (
        session.laps
        .pick_drivers(DRIVER)
        .pick_laps(LAP_NUMBER)
        .iloc[0]
    )

    print()
    print("=" * 100)
    print(
        f"{YEAR} Round {ROUND} | {DRIVER} | Lap {LAP_NUMBER}"
    )
    print("=" * 100)
    print()

    for column in lap.index:

        print_value(
            column,
            lap[column]
        )

    print()
    print("=" * 100)
    print("LAP OBJECT")
    print("=" * 100)

    print(type(lap))

    print()
    print("=" * 100)
    print("AVAILABLE METHODS")
    print("=" * 100)

    methods = [
        name
        for name in dir(lap)
        if not name.startswith("_")
    ]

    for method in sorted(methods):

        print(method)


if __name__ == "__main__":
    main()