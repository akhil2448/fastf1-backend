import pandas as pd
import math


def build_track_status_json(track_status_df, session, calendar_date):
    """
    Event-based track status synced to race clock.
    - RaceSecond 0 is ALWAYS AllClear
    - Ignore all events before race start
    """

    # --- Determine race start time (Lap 1 start) ---
    race_start_time = (
        session.laps
        .loc[session.laps["LapNumber"] == 1, "LapStartTime"]
        .min()
    )

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

    # --- Always start with AllClear at race second 0 ---
    track_status_json["trackStatusData"].append({
        "raceSecond": 0,
        "trackStatus": 1
    })

    # --- Process only events AFTER race start ---
    for _, row in track_status_df.iterrows():
        time = row["Time"]

        if time is None or pd.isna(time):
            continue

        time = pd.to_timedelta(time)

        # Ignore pre-race events
        if time <= race_start_time:
            continue

        race_second = math.floor(
            (time - race_start_time).total_seconds()
        )

        track_status_json["trackStatusData"].append({
            "raceSecond": race_second,
            "trackStatus": int(row["Status"])
        })

    # --- Ensure chronological order ---
    track_status_json["trackStatusData"].sort(
        key=lambda x: x["raceSecond"]
    )

    return track_status_json
