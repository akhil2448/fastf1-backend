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
session = fastf1.get_session(2023, 15, 'Race')
session.load()
session.results.to_csv("2023_sing.csv", index= False)

# # Get the specific driver by their three-letter code (e.g., 'HAM')
# driver_info = session.get_driver('HAM')

# print(driver_info['FullName'])
# print(driver_info['LastName'])
# print(driver_info['CountryCode'])


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

# The event schedule provides the official length in kilometers
import fastf1

session = fastf1.get_session(2024, 'Spanish Grand Prix', 'R')
session.load()

# Print the entire event series to see available column attributes
print(session.event)


# %%
import fastf1

session = fastf1.get_session(2024, 'Spanish Grand Prix', 'Q')
session.load()

# 1. Get raw telemetry distance
lap = session.laps.pick_fastest()
telemetry = lap.get_car_data().add_distance()
raw_telemetry_length = telemetry['Distance'].max()

# 2. Get the lowercase circuit info corners dataframe
circuit_info = session.get_circuit_info()

# Get the count from the index of the dataframe
number_of_corners = len(circuit_info.corners)

# 3. Apply the corner-density offset rule
# We add back ~1.05 meters per corner to counteract apex cutting
estimated_offset = number_of_corners * 1.05
closer_accurate_length = raw_telemetry_length + estimated_offset

print(f"Raw Telemetry Length: {raw_telemetry_length:.2f} m")
print(f"Number of Corners: {number_of_corners}")
print(f"Estimated True Length: {closer_accurate_length:.2f} m")
# This should scale Barcelona up from ~4642m closer to the official 4657m


# %%
import fastf1

# Define our test batch (Year, Event Name, Official FIA Length)
test_tracks = [
    {"year": 2024, "event": "Italian Grand Prix", "official": 5793, "type": "High Speed (Monza)"},
    {"year": 2024, "event": "Monaco Grand Prix", "official": 3337, "type": "Street Circuit (Monaco)"},
    {"year": 2024, "event": "Belgian Grand Prix", "official": 7004, "type": "Long Sweeper (Spa)"}
]

for track in test_tracks:
    try:
        session = fastf1.get_session(track["year"], track["event"], 'Q')
        session.load(telemetry=True)
        
        # 1. Get raw distance
        lap = session.laps.pick_fastest()
        telemetry = lap.get_car_data().add_distance()
        raw_len = telemetry['Distance'].max()
        
        # 2. Get corner count
        circuit_info = session.get_circuit_info()
        corners = len(circuit_info.corners)
        
        # 3. Analyze the current error per corner
        total_missing_distance = track["official"] - raw_len
        ideal_constant_for_this_track = total_missing_distance / corners
        
        print(f"--- {track['type']} ---")
        print(f"Corners: {corners} | Missing Distance: {total_missing_distance:.2f}m")
        print(f"Ideal constant for this specific track: {ideal_constant_for_this_track:.2f}\n")
    except Exception as e:
        print(f"Error loading {track['event']}: {e}")

# %%

import fastf1

session = fastf1.get_session(2025, 18, 'Q')
session.load(telemetry=True)

lap = session.laps.pick_fastest()
telemetry = lap.get_car_data().add_distance()
raw_telemetry_length = telemetry['Distance'].max()

circuit_info = session.get_circuit_info()
number_of_corners = len(circuit_info.corners)

# Refined algorithm: Fixed telemetry offset + corner scaling
estimated_length = raw_telemetry_length + (number_of_corners * 4.0)

print(f"Raw Telemetry Length: {raw_telemetry_length:.2f} m")
print(f"Refined Estimated Length: {estimated_length:.2f} m")

# %%
import fastf1

YEAR = 2018
ROUND = 10

session = fastf1.get_session(YEAR, ROUND, "R")
session.load()

print(f"Race: {session.event['EventName']}")
print()

for _, result in session.results.iterrows():
    driver_number = result["DriverNumber"]
    driver = result["Abbreviation"]

    driver_laps = session.laps.pick_drivers(driver_number)

    print("=" * 80)
    print(
        f"{driver} "
        f"(Completed: {result['Laps']} laps, "
        f"Recorded: {len(driver_laps)} laps)"
    )

    print()

    # print(
    #     driver_laps[
    #         [
    #             "LapNumber",
    #             "Stint",
    #             "Compound",
    #             "FreshTyre",
    #             "PitOutTime",
    #             "PitInTime",
    #         ]
    #     ].to_string(index=False)
    # )

    # print()

    # print("Grouped by stint:")

    # for stint, stint_df in driver_laps.groupby("Stint"):
    #     print(
    #         f"Stint {stint}: "
    #         f"{int(stint_df['LapNumber'].min())}"
    #         f"-"
    #         f"{int(stint_df['LapNumber'].max())}"
    #         f" "
    #         f"({len(stint_df)} recorded laps)"
    #     )

    # print()
    
    for stint, stint_df in driver_laps.groupby("Stint", dropna=False):
        print(stint)
        print(stint_df["LapNumber"].tolist())
# %%

import fastf1 as f1
import pandas as pd


# Load the Race session (e.g., 2026 Round 1)
race = f1.get_session(2026, 2, 'R')
race.load()

# 1. Fetch the starting grid base data
starting_grid = race.results[['DriverId', 'GridPosition', 'FullName', 'TeamName']].copy()

# 2. Extract the compound used on Lap 1 for each driver
# Filter laps to only include the opening lap of the race
lap_one = race.laps.pick_lap(1)[['DriverNumber', 'Compound', 'FreshTyre']]

# Note: race.results uses 'DriverId' (e.g., 'HAM') while race.laps uses 'DriverNumber' (e.g., '44')
# We map them together using FastF1's internal driver mapping
driver_mapping = race.results[['DriverId', 'DriverNumber']]
lap_one = lap_one.merge(driver_mapping, on='DriverNumber')

# 3. Merge tire data back into the starting grid DataFrame
final_grid = starting_grid.merge(lap_one[['DriverId', 'Compound', 'FreshTyre']], on='DriverId')

# 4. Clean up, sort, and display from Pole Position to last
final_grid['GridPosition'] = final_grid['GridPosition'].astype(int)
final_grid = final_grid.sort_values(by='GridPosition').reset_index(drop=True)

print(final_grid)
# %%
import fastf1

session = fastf1.get_session(2018, 21, "R")
session.load()

print("Drivers:")
print(session.drivers)
print()

print("Position data keys:")
print(sorted(session.pos_data.keys()))
print()

print("Car data keys:")
print(sorted(session.car_data.keys()))
# %%
for driver in sorted(session.laps["Driver"].unique()):
    print(f"\n===== {driver} =====")

    try:
        laps = session.laps.pick_drivers([driver])

        drv = session.get_driver(driver)
        number = drv["DriverNumber"]

        print(f"Driver number: {number}")

        telemetry = laps.get_telemetry()

        print(f"Telemetry rows: {len(telemetry)}")

    except Exception as e:
        import traceback

        print(f"FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
# %%
driver = "VER"

info = session.get_driver(driver)

print(info)
print()

print("Driver number:", info["DriverNumber"])
print()

print("Driver number in pos_data:",
      info["DriverNumber"] in session.pos_data)

print("Driver number in car_data:",
      info["DriverNumber"] in session.car_data)

print()

print("Available pos_data keys:")
print(sorted(session.pos_data.keys()))
# %%
