#%%
import fastf1;
import pandas as pd

fastf1.Cache.enable_cache("cache")  # local cache folder

# session = fastf1.get_session(2023, 3, 'R')

# Load only metadata (FAST)
# session.load(laps=True, telemetry=True, weather=True)

# session.load(laps=True)
# driver_number = '1' # Max Verstappen's number
# driver_info = session.get_driver(driver_number)
# print(driver_info['FullName']) # Output: Max Verstappen

# Load session (e.g., 2024 British Grand Prix)
session = fastf1.get_session(2024, 'British Grand Prix', 'Race')
session.load()
session.results.to_csv("2026_chi.csv", index= False)

# Get the specific driver by their three-letter code (e.g., 'HAM')
driver_info = session.get_driver('HAM')

print(driver_info['FullName'])
print(driver_info['LastName'])
print(driver_info['CountryCode'])


#%%
def build_track_status_per_second(session):
    session.load(laps=True, telemetry=True, weather=True)

    # 2. Determine race start time (same as telemetry)
    race_start_time = (
        session.laps
        .loc[session.laps["LapNumber"] == 1, "LapStartTime"]
        .min()
    )

    # 3. Extract time + status
    df = session.laps[["Time", "TrackStatus"]].copy()
    df = df.dropna(subset=["Time", "TrackStatus"])

    # 4. Convert to race-relative seconds
    df["RaceSecond"] = (
        (df["Time"] - race_start_time)
        .dt.total_seconds()
        .astype(int)
    )

    df = df[df["RaceSecond"] >= 0]

    # 5. Sort by time (important!)
    df = df.sort_values("RaceSecond")

    # 6. One record per second (last known status)
    per_second = (
        df.groupby("RaceSecond")["TrackStatus"]
        .last()
        .reset_index()
    )

    # 7. Carry forward missing seconds
    max_second = per_second["RaceSecond"].max()

    timeline = []
    current_status = int(per_second.iloc[0]["TrackStatus"])
    idx = 0

    for second in range(max_second + 1):
        if idx < len(per_second) and per_second.iloc[idx]["RaceSecond"] == second:
            current_status = int(per_second.iloc[idx]["TrackStatus"])
            idx += 1

        timeline.append({
            "raceSecond": second,
            "trackStatus": current_status
        })

    return timeline


data = build_track_status_per_second(session)
print(data)
# %%
session.laps.to_csv("2023_aus.csv", index= False)

# %%

import fastf1;
import pandas as pd

fastf1.Cache.enable_cache("cache")  # local cache folder

session = fastf1.get_session(2020, 3, 'R')
session.load(laps=True, telemetry=True)

session.laps.to_csv("2020_03.csv", index=False)

# circuit_info = session.get_circuit_info()
# print(circuit_info)


# lap = session.laps.pick_drivers("MSC")
# telemetry = lap.get_telemetry()
# telemetry.to_csv("telemetry_data_MSC_7_2021.csv", index=False)

# # same as session.session_start_time
# race_start_time = (
#         session.laps
#         .loc[session.laps["LapNumber"] == 1, "LapStartTime"]
#         .min())

# print("Session time when race started: ", race_start_time)
# print(session.date)
# print("temp " ,session.t0_date)
# session.get_circuit_info

# race_start_utc = session.t0_date + race_start_time
# print(race_start_utc)


# schedule = fastf1.get_event_schedule(2025)

# row = schedule.loc[schedule["RoundNumber"] == 3].iloc[0]

# local_dt = pd.to_datetime(row["Session5Date"])     # tz-aware
# utc_dt   = pd.to_datetime(row["Session5DateUtc"])  # naive UTC

# offset = local_dt.utcoffset()
# print(offset)  # datetime.timedelta(seconds=7200) → +02:00

# race_start_local = session.t0_date + race_start_time + offset

# print(race_start_local)
# fastf1.get_event_schedule(2025)

# session.results
# %%
import fastf1

YEAR = 2021
ROUND = 8  # Styrian GP
SESSION = "Q"

session = fastf1.get_session(YEAR, ROUND, SESSION)
session.load()

circuit_info = session.get_circuit_info()

print(circuit_info.corners)
# %%
import fastf1

year = 2020
round_number = 2

session = fastf1.get_session(year, round_number, "Q")
session.load()

lap = (
    session.laps
    .pick_drivers("HAM")
    .pick_fastest()
)

print("Available columns:")
print(lap.index.tolist())

print("\n============================")
print("Tyre-related fields")
print("============================")

for column in [
    "Compound",
    "TyreLife",
    "FreshTyre",
    "Stint",
    "LapNumber",
]:
    if column in lap.index:
        print(f"{column:12}: {lap[column]}")
    else:
        print(f"{column:12}: <NOT PRESENT>")
# %%
