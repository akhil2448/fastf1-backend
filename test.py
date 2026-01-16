#%%
import fastf1;
import pandas as pd

fastf1.Cache.enable_cache("cache")  # local cache folder

session = fastf1.get_session(2023, 3, 'R')

# Load only metadata (FAST)
# session.load(laps=True, telemetry=True, weather=True)


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

session = fastf1.get_session(2023, 3, 'R')
session.load(laps=True, telemetry=True, weather=True)

race_start_time = (
        session.laps
        .loc[session.laps["LapNumber"] == 1, "LapStartTime"]
        .min())

print(race_start_time)

session.track_status

# session.get_circuit_info
# %%
