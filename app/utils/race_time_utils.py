import fastf1
import pandas as pd
from datetime import timezone


def get_local_race_start_time_str(session, calendar_year: int) -> str:
    """
    Returns local race start time as JSON-safe string: HH:mm:ss.SSS

    - Uses Lap 1 earliest LapStartTime (actual race start)
    - Anchors to session.t0_date (UTC)
    - Applies the exact UTC offset used for that race from event schedule
    - No timezone hardcoding
    """

    # --- race start in session time ---
    race_start_time = (
        session.laps
        .loc[session.laps["LapNumber"] == 1, "LapStartTime"]
        .min()
    )

    # --- convert to UTC wall-clock ---
    race_start_utc = (
        session.t0_date + race_start_time
    ).replace(tzinfo=timezone.utc)

    # --- get schedule row for this event ---
    schedule = fastf1.get_event_schedule(calendar_year)

    event_row = schedule.loc[
        schedule["EventName"] == session.event["EventName"]
    ].iloc[0]

    # --- derive offset used at that race ---
    local_sched = pd.to_datetime(event_row["Session5Date"])     # tz-aware
    offset = local_sched.utcoffset()

    # --- apply offset ---
    race_start_local = race_start_utc + offset

    # --- JSON-safe time string ---
    return race_start_local.strftime("%H:%M:%S.%f")[:-3]
