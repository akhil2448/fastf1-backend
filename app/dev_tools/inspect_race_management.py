import fastf1
import pandas as pd

YEAR = 2024
ROUND = 11  # Austria


def print_section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def main():
    fastf1.Cache.enable_cache("cache")

    print(f"Loading Race {YEAR} Round {ROUND}...")

    session = fastf1.get_session(YEAR, ROUND, "R")
    session.load(
        laps=True,
        telemetry=False,
        weather=True,
        messages=True
    )

    ####################################################################################
    # Session
    ####################################################################################

    print_section("SESSION INFO")

    print(session)
    print()
    print("Event")
    print(session.event)

    ####################################################################################
    # Drivers
    ####################################################################################

    print_section("DRIVERS")

    print(session.drivers)

    for drv in session.drivers:
        info = session.get_driver(drv)

        print(info)

    ####################################################################################
    # LAPS
    ####################################################################################

    print_section("LAPS DATAFRAME")

    print(session.laps.head())

    print()

    print("Columns")

    for col in session.laps.columns:
        print(col)

    print()

    print(session.laps.info())

    ####################################################################################
    # SAMPLE LAP
    ####################################################################################

    print_section("FIRST VALID LAP")

    valid = session.laps.pick_quicklaps()

    if not valid.empty:

        lap = valid.iloc[0]

        for key, value in lap.items():
            print(f"{key:25}: {value}")

    ####################################################################################
    # STINT INFORMATION
    ####################################################################################

    print_section("STINT SUMMARY")

    for drv in session.drivers:

        driver_laps = session.laps.pick_drivers(drv)

        print(f"\nDriver {drv}")

        stints = (
            driver_laps.groupby("Stint")
            .agg(
                Compound=("Compound", "first"),
                Laps=("LapNumber", "count"),
                StartLap=("LapNumber", "min"),
                EndLap=("LapNumber", "max"),
                TyreLife=("TyreLife", "max"),
                FreshTyre=("FreshTyre", "first"),
            )
        )

        print(stints)

    ####################################################################################
    # WEATHER
    ####################################################################################

    print_section("WEATHER")

    print(session.weather_data.head())

    print()

    print(session.weather_data.columns)

    ####################################################################################
    # RACE CONTROL
    ####################################################################################

    print_section("RACE CONTROL MESSAGES")

    if session.race_control_messages is not None:
        print(session.race_control_messages.head())
        print(session.race_control_messages.columns)

    ####################################################################################
    # TRACK STATUS
    ####################################################################################

    print_section("TRACK STATUS")

    try:

        sample = session.laps.iloc[20]

        print(sample["TrackStatus"])

        print()

        statuses = session.laps["TrackStatus"].unique()

        print("Unique statuses")

        print(statuses)

    except Exception as e:
        print(e)

    ####################################################################################
    # LAP BY LAP
    ####################################################################################

    print_section("ONE DRIVER LAP TABLE")

    drv = session.drivers[0]

    laps = session.laps.pick_drivers(drv)

    cols = [
        "LapNumber",
        "LapTime",
        "Stint",
        "Compound",
        "TyreLife",
        "FreshTyre",
        "Position",
        "TrackStatus",
        "PitInTime",
        "PitOutTime",
        "IsPersonalBest",
        "Deleted",
        "FastF1Generated",
    ]

    existing = [c for c in cols if c in laps.columns]

    print(laps[existing])

    ####################################################################################
    # TELEMETRY COLUMNS
    ####################################################################################

    print_section("TELEMETRY")

    lap = valid.iloc[0]

    telemetry = lap.get_car_data()

    print(telemetry.head())

    print()

    print("Telemetry Columns")

    for col in telemetry.columns:
        print(col)

    print()

    print(telemetry.info())

    ####################################################################################
    # POSITION DATA
    ####################################################################################

    print_section("POSITION DATA")

    position = lap.get_pos_data()

    print(position.head())

    print()

    for col in position.columns:
        print(col)

    print(position.info())


if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 250)

    main()