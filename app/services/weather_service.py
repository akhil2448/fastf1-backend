import pandas as pd


def build_weather_json(weather_df, session, calendar_date):
    weather_df = weather_df.where(weather_df.notna(), None)

    # --- Determine race start time (Lap 1 start) ---
    race_start_time = (
        session.laps
        .loc[session.laps["LapNumber"] == 1, "LapStartTime"]
        .min()
    )

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

        time = row["Time"]

        if time is None or pd.isna(time):
            continue

        time = pd.to_timedelta(time)

        # Ignore pre-race weather samples
        if time < race_start_time:
            continue

        race_second = round(
            (time - race_start_time).total_seconds()
        )

        weather_json["weatherData"].append({
            "raceSecond": race_second,

            "AirTemp": row["AirTemp"],
            "Humidity": row["Humidity"],
            "Pressure": row["Pressure"],

            "Rainfall": row["Rainfall"],

            "TrackTemp": row["TrackTemp"],

            "WindDirection": row["WindDirection"],
            "WindSpeed": row["WindSpeed"]
        })

    return weather_json