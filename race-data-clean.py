#%%
import fastf1
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

fastf1.Cache.enable_cache("cache")  # local cache folder

session = fastf1.get_session(2021, 7, 'R')

# Load only metadata (FAST)
session.load(laps=True, telemetry=True, weather=True)
laps = session.laps
weather_data = session.laps.get_weather_data()
laps = laps.reset_index(drop=True)
weather_data = weather_data.reset_index(drop=True)

lapsAndWeatherDatajoined = pd.concat([laps, weather_data.loc[:, ~(weather_data.columns == 'Time')]], axis=1)
laps = lapsAndWeatherDatajoined[
    ["DriverNumber", "Driver", "Team", "LapNumber", "LapTime",
      "IsPersonalBest", "PitInTime", "PitOutTime",
          "Time", "LapStartTime", "Position", "Compound", "TyreLife"]
]

## Time Converter
def timedelta_to_hms_micro(td):
    if pd.isna(td):
        return None

    total_microseconds = int(td.total_seconds() * 1_000_000)

    hours, remainder = divmod(total_microseconds, 3_600_000_000)
    minutes, remainder = divmod(remainder, 60_000_000)
    seconds, microseconds = divmod(remainder, 1_000_000)

    return f"{hours:02}:{minutes:02}:{seconds:02}.{microseconds:06d}"


## Detect all Timedelta columns automatically
def convert_all_timedelta_columns(df):
    for col in df.select_dtypes(include=["timedelta64[ns]"]).columns:
        df[col] = df[col].apply(timedelta_to_hms_micro)
    return df

laps = convert_all_timedelta_columns(laps)

def generate_race_json(laps, session, calendar_date):
    race_json = {
        "session": {
            "year": calendar_date.year,
            "Date": f"{calendar_date.month}/{calendar_date.day}",
            "event": session.event["EventName"],
            "location": session.event["Location"],
            "type": "Race"
        },
        "drivers": {}
    }

    lap_columns = [
        "LapNumber",
        "LapTime",
        "Time",
        "LapStartTime",
        "Position",
        "TyreLife"
    ]

    for driver, df in laps.groupby("Driver"):
        df = df.where(df.notna(), None).sort_values("LapNumber")

        driver_block = {
            "DriverNumber": df.iloc[0]["DriverNumber"],
            "Team": df.iloc[0]["Team"],
            "laps": [],
            "PitStopData": [],
            "PersonalBestLaps": []
        }

        for _, row in df.iterrows():
            lap_number = row["LapNumber"]

            # -------- laps[] --------
            lap_data = {col: row[col] for col in lap_columns}
            driver_block["laps"].append(lap_data)

            # -------- PitStopData[] --------
            is_start_lap = lap_number == 1
            has_pit_event = row["PitInTime"] is not None or row["PitOutTime"] is not None

            if is_start_lap or has_pit_event:
                driver_block["PitStopData"].append({
                    "LapNumber": lap_number,
                    "PitInTime": row["PitInTime"],
                    "PitOutTime": row["PitOutTime"],
                    "Compound": row["Compound"]
                })

            # -------- PersonalBestLaps[] --------
            if row["IsPersonalBest"] is True:
                driver_block["PersonalBestLaps"].append(lap_number)

        race_json["drivers"][driver] = driver_block

    return race_json

## Calling generata_race_json function and generate JSON
# calendarDate = session.event["EventDate"].date()

# race_json = generate_race_json(
#     laps=laps,
#     session=session,
#     calendar_date=calendarDate
# )

# with open("race.json", "w") as f:
#     json.dump(race_json, f, indent=2)

##lapsAndWeatherDatajoined.to_csv("data.csv", index=False)


### Weather Data

## Weather data provides the following data channels per sample:
# Time (datetime.timedelta): session timestamp (time only)
# AirTemp (float): Air temperature [°C]
# Humidity (float): Relative humidity [%]
# Pressure (float): Air pressure [mbar]
# Rainfall (bool): Shows if there is rainfall
# TrackTemp (float): Track temperature [°C]
# WindDirection (int): Wind direction [°] (0°-359°)
# WindSpeed (float): Wind speed [m/s]
# Weather data is updated once per minute.

weatherData = convert_all_timedelta_columns(session._weather_data)


## Build Weather data
def build_weather_json(weather_df, session, calendar_date):
    """
    Converts FastF1 weather dataframe into structured JSON-ready dict
    """

    # Ensure JSON-safe values (NaN -> None)
    weather_df = weather_df.where(weather_df.notna(), None)

    weather_json = {
        "session": {
            "year": calendar_date.year,
            "Date": f"{calendar_date.month}/{calendar_date.day}",
            "event": session.event["EventName"],
            "location": session.event["Location"],
            "type": "Race"
        },
        "weatherData": []
    }

    for _, row in weather_df.iterrows():
        weather_json["weatherData"].append({
            "Time": row["Time"],
            "AirTemp": row["AirTemp"],
            "Humidity": row["Humidity"],
            "Pressure": row["Pressure"],
            "Rainfall": row["Rainfall"],
            "TrackTemp": row["TrackTemp"],
            "WindDirection": row["WindDirection"],
            "WindSpeed": row["WindSpeed"]
        })

    return weather_json

## Calling build_weather_data function and generate JSON
# calendarDate = session.event["EventDate"].date()

# weather_json = build_weather_json(
#     weather_df=weatherData,
#     session=session,
#     calendar_date=calendarDate
# )

# with open("weather.json", "w") as f:
#     json.dump(weather_json, f, indent=2)



### TrackStatus
# Track status contains information on yellow/red/green flags, safety car and virtual safety car. It provides the following data channels per sample:
# Time (datetime.timedelta): session timestamp (time only)
# Status (str): contains track status changes as numeric values (described below)
# Message (str): contains the same information as status but in easily understandable words (‘Yellow’, ‘AllClear’,…)
# A new value is sent every time the track status changes.
# Track status is indicated using single digit integer status codes (as string). List of known statuses:
# ‘1’: Track clear (beginning of session or to indicate the end
# of another status)
# ‘2’: Yellow flag (sectors are unknown)
# ‘3’: ??? Never seen so far, does not exist?
# ‘4’: Safety Car
# ‘5’: Red Flag
# ‘6’: Virtual Safety Car deployed
# ‘7’: Virtual Safety Car ending (As indicated on the drivers steering wheel, on tv and so on; status ‘1’ will mark the actual end)

trackStatus = convert_all_timedelta_columns(lapsAndWeatherDatajoined[["Time", "TrackStatus"]])

## Build Track Status data
def build_track_status_json(track_status_df, session, calendar_date):
    """
    Converts track status dataframe into JSON-ready dict
    """

    # Ensure JSON-safe values
    track_status_df = track_status_df.where(track_status_df.notna(), None)

    track_status_json = {
        "session": {
            "year": calendar_date.year,
            "Date": f"{calendar_date.month}/{calendar_date.day}",
            "event": session.event["EventName"],
            "location": session.event["Location"],
            "type": "Race"
        },
        "trackStatusData": []
    }

    for _, row in track_status_df.iterrows():
        track_status_json["trackStatusData"].append({
            "Time": row["Time"],
            "TrackStatus": int(row["TrackStatus"]) if row["TrackStatus"] is not None else None
        })

    return track_status_json

## Calling track_status_json function to generate JSON
# calendarDate = session.event["EventDate"].date()

# track_status_json = build_track_status_json(
#     track_status_df=trackStatus,
#     session=session,
#     calendar_date=calendarDate
# )

# with open("track_status.json", "w") as f:
#     json.dump(track_status_json, f, indent=2)


# ### Generate Circuit map
def generate_track_map(session, include_start_point=True,
                       save_to_file=False, filename="track_map.json"):
    """
    Generates a track map from FastF1 telemetry using the fastest lap.

    Returns:
        List of dicts:
        [
          { "x": float, "y": float, "isStart": bool },
          ...
        ]
    """

    # Pick fastest lap for clean racing line
    lap = session.laps.pick_fastest()

    # Get telemetry (position data)
    telemetry = lap.get_telemetry()[["X", "Y", "Distance"]]

    # Ensure correct start ordering
    telemetry = telemetry.sort_values("Distance")

    # Get circuit rotation info
    circuit_info = session.get_circuit_info()
    angle = np.deg2rad(circuit_info.rotation)

    rotation_matrix = np.array([
        [np.cos(angle), np.sin(angle)],
        [-np.sin(angle), np.cos(angle)]
    ])

    # Rotate track coordinates
    rotated = telemetry[["X", "Y"]].to_numpy().dot(rotation_matrix)

    track_map = []

    for idx, (x, y) in enumerate(rotated):
        point = {
            "x": float(x),
            "y": float(y)
        }

        if include_start_point and idx == 0:
            point["isStart"] = True

        track_map.append(point)

    # Optional save to file
    if save_to_file:
        with open(filename, "w") as f:
            json.dump(track_map, f, indent=2)

    return track_map

## Call generate_track_map
# track_map = generate_track_map(
#     session=session,
#     save_to_file=True,
#     filename="track_map.json"
# )

def visualize_track_map(track_map, title="Track Map"):
    """
    Visualizes a track map and highlights the start point.
    """

    x = [p["x"] for p in track_map]
    y = [p["y"] for p in track_map]

    start_point = next((p for p in track_map if p.get("isStart")), None)

    plt.figure(figsize=(10, 8))
    plt.plot(x, y, color="black", linewidth=2)

    if start_point:
        plt.scatter(
            start_point["x"],
            start_point["y"],
            color="red",
            s=100,
            zorder=5,
            label="Start / Finish"
        )

    plt.axis("equal")
    plt.axis("off")
    plt.title(title)
    if start_point:
        plt.legend()

    plt.show()

# ## Calling plot_track_map
# visualize_track_map(
#     track_map=track_map,
#     title="2021 French Grand Prix – Track Map"
# )

# %%

# timeStamp = session.event["EventDate"]
# date = timeStamp.date()
# f"{date.month}/{date.day}"

#session._weather_data.to_csv("weather-data.csv", index=False)

# trackStatus = convert_all_timedelta_columns(lapsAndWeatherDatajoined[["Time", "TrackStatus"]])
# trackStatus

# %%

session = fastf1.get_session(2021, 7, 'R')

session.event["EventName"]
session.event["Location"]
session.event["Country"]
session.event["OfficialEventName"]
# %%
lap = session.laps.pick_drivers("HAM")
telemetry = lap.get_telemetry()
telemetry.to_csv("telemetry_data_ham_2021.csv", index=False)
session.laps.to_csv("race_data_2021.csv", index=False)
# %%
