import fastf1
import pandas as pd

YEAR = 2024
ROUND = 11
DRIVER = "HAM"   # Change this to inspect another driver


def td_to_seconds(td):
    if pd.isna(td):
        return None
    return round(td.total_seconds(), 3)


def print_header():
    print("=" * 170)
    print(
        f"{'Lap':>3} | "
        f"{'Stint':>5} | "
        f"{'Compound':>8} | "
        f"{'Age':>3} | "
        f"{'Fresh':>5} | "
        f"{'LapTime':>8} | "
        f"{'Pos':>3} | "
        f"{'Track':>6} | "
        f"{'PitOut':>6} | "
        f"{'PitIn':>5} | "
        f"{'Deleted':>7} | "
        f"{'Accurate':>8}"
    )
    print("=" * 170)


def main():

    fastf1.Cache.enable_cache("cache")

    session = fastf1.get_session(YEAR, ROUND, "R")

    session.load(
        laps=True,
        telemetry=False,
        weather=False,
        messages=False,
    )

    laps = session.laps.pick_drivers(DRIVER)

    print(f"\nDriver: {DRIVER}")
    print_header()

    for _, lap in laps.iterrows():

        print(
            f"{int(lap['LapNumber']):>3} | "
            f"{int(lap['Stint']):>5} | "
            f"{lap['Compound']:>8} | "
            f"{int(lap['TyreLife']):>3} | "
            f"{str(lap['FreshTyre']):>5} | "
            f"{td_to_seconds(lap['LapTime']):>8} | "
            f"{int(lap['Position']):>3} | "
            f"{lap['TrackStatus']:>6} | "
            f"{str(pd.notna(lap['PitOutTime'])):>6} | "
            f"{str(pd.notna(lap['PitInTime'])):>5} | "
            f"{str(lap['Deleted']):>7} | "
            f"{str(lap['IsAccurate']):>8}"
        )


if __name__ == "__main__":
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)

    main()