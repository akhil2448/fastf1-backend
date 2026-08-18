import fastf1
import pandas as pd

fastf1.Cache.enable_cache("cache")

session = fastf1.get_session(2021, 21, "R")
session.load()

laps = session.laps.pick_driver("VER")

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 250)

print(
    laps[
        [
            "LapNumber",
            "LapTime",
            "Sector1Time",
            "Sector2Time",
            "Sector3Time",
            "Time",
            "LapStartTime",
            "PitInTime",
            "PitOutTime",
            "TrackStatus",
            "Deleted",
            "IsAccurate",
        ]
    ]
)

print("\n==============================")
print("Laps with missing LapTime")
print("==============================")

missing = laps[laps["LapTime"].isna()]

print(
    missing[
        [
            "LapNumber",
            "Sector1Time",
            "Sector2Time",
            "Sector3Time",
            "Time",
            "TrackStatus",
            "Deleted",
            "IsAccurate",
        ]
    ]
)

print("\n==============================")
print("Sector Sum")
print("==============================")

for _, lap in laps.iterrows():

    if (
        pd.notna(lap["Sector1Time"])
        and pd.notna(lap["Sector2Time"])
        and pd.notna(lap["Sector3Time"])
    ):

        sector_sum = (
            lap["Sector1Time"]
            + lap["Sector2Time"]
            + lap["Sector3Time"]
        )

        print(
            f"Lap {int(lap['LapNumber']):2d}"
            f" | LapTime={lap['LapTime']}"
            f" | SectorSum={sector_sum}"
        )