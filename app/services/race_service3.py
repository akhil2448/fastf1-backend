import pandas as pd
from app.utils.time_utils import convert_all_timedelta_columns


def _to_timedelta_safe(value):
    """
    Always returns pd.Timedelta or None
    Works for:
    - pd.Timedelta
    - '0 days 00:00:22.123000'
    - None
    """
    if value is None or pd.isna(value):
        return None
    if isinstance(value, pd.Timedelta):
        return value
    return pd.to_timedelta(value)


def generate_race_json(laps, session, calendar_date):
    # Defensive copy
    laps = laps.copy()

    # We ARE calling this as you requested
    laps = convert_all_timedelta_columns(laps)

    race_json = {
        "session": {
            "year": calendar_date.year,
            "Date": f"{calendar_date.month}/{calendar_date.day}",
            "event": session.event["EventName"],
            "location": session.event["Location"],
            "type": "Race",
            "totalLaps": session.total_laps
        },
        "drivers": {}
    }

    lap_columns = [
        "LapNumber",
        "TyreLife"
    ]

    for (driver, driver_number), df in laps.groupby(["Driver", "DriverNumber"]):
        df = df.where(df.notna(), None).sort_values("LapNumber")

        driver_block = {
            "DriverNumber": driver_number,
            "Team": df.iloc[0]["Team"],
            "laps": [],
            "PitStopData": [],
            "PersonalBestLaps": []
        }

        previous_pit_in_time = None

        for _, row in df.iterrows():
            lap_number = int(row["LapNumber"])

            # -------- laps[] --------
            driver_block["laps"].append({
                "LapNumber": lap_number,
                "TyreLife": row["TyreLife"]
            })

            # -------- PitStopData[] --------
            pit_in_time = _to_timedelta_safe(row["PitInTime"])
            pit_out_time = _to_timedelta_safe(row["PitOutTime"])

            is_in_pit = False
            is_out_pit = False
            total_pit_time = 0

            # Lap 1 → starting tyre
            if lap_number == 1:
                driver_block["PitStopData"].append({
                    "LapNumber": lap_number,
                    "IsInPit": False,
                    "IsOutPit": False,
                    "TotalPitTime": 0,
                    "Compound": row["Compound"]
                })
                continue

            # Pit IN
            if pit_in_time is not None:
                is_in_pit = True
                previous_pit_in_time = pit_in_time

            # Pit OUT
            if pit_out_time is not None and previous_pit_in_time is not None:
                is_out_pit = True
                total_pit_time = (
                    pit_out_time - previous_pit_in_time
                ).total_seconds()

            if is_in_pit or is_out_pit:
                driver_block["PitStopData"].append({
                    "LapNumber": lap_number,
                    "IsInPit": is_in_pit,
                    "IsOutPit": is_out_pit,
                    "TotalPitTime": total_pit_time,
                    "Compound": row["Compound"]
                })

            # -------- PersonalBestLaps[] --------
            if row["IsPersonalBest"] is True:
                driver_block["PersonalBestLaps"].append(lap_number)

        race_json["drivers"][driver] = driver_block

    return race_json
