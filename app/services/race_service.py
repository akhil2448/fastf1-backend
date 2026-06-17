import pandas as pd
import math
from app.services.compute_sector_distances import compute_sector_distance_ratios
from app.utils.race_time_utils import get_local_race_start_time_str

RED_FLAG_RESUME_BUFFER_SECONDS = 8

def _to_timedelta_safe(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, pd.Timedelta):
        return value
    return pd.to_timedelta(value)


def _normalize_timestamp(td, race_start_time):
    """
    Normalize session timestamp → race seconds
    """
    if td is None:
        return None
    return (td - race_start_time).total_seconds()


def _duration_seconds(td):
    """
    Convert duration → seconds
    """
    if td is None:
        return None
    return td.total_seconds()


def _safe_int(value):
    return int(value) if pd.notna(value) else None

def build_red_flag_metadata(
    laps,
    track_status_df,
    race_start_time
):
    """
    Build replay-specific red flag restart metadata.

    Logic:
    - Find all RED FLAG declarations (Status == 5)
    - Find minimum lapStartTime strictly AFTER red flag
    - Compute replay resume point
    """

    red_flags = []

    # --- Find RED FLAG events ---
    red_flag_events = track_status_df[
        track_status_df["Status"].astype(str) == "5"
    ]

    for idx, (_, row) in enumerate(red_flag_events.iterrows(), start=1):
        time = row.get("Time")

        if time is None or pd.isna(time):
            continue

        time = pd.to_timedelta(time)

        # Normalize to race second
        red_flag_race_second = math.floor(
            (time - race_start_time).total_seconds()
        )

        # --- Find all lapStartTimes AFTER red flag ---
        candidate_lap_times = []

        for _, lap_row in laps.iterrows():
            lap_start = lap_row.get("LapStartTime")

            if lap_start is None or pd.isna(lap_start):
                continue

            lap_start = pd.to_timedelta(lap_start)

            normalized_lap_start = (
                lap_start - race_start_time
            ).total_seconds()

            # STRICTLY after red flag
            if normalized_lap_start > red_flag_race_second:
                candidate_lap_times.append({
                    "lap": int(lap_row["LapNumber"]),
                    "lapStartTime": normalized_lap_start
                })

        if not candidate_lap_times:
            continue

        # --- Find earliest competitive lap restart ---
        earliest_restart = min(
            candidate_lap_times,
            key=lambda x: x["lapStartTime"]
        )

        competitive_lap_start = round(
            earliest_restart["lapStartTime"],
            3
        )

        resume_race_second = max(
            0,
            math.floor(
                competitive_lap_start
                - RED_FLAG_RESUME_BUFFER_SECONDS
            )
        )

        red_flags.append({
            "id": f"RF_{idx}",

            "redFlagRaceSecond": red_flag_race_second,

            "restart": {
                "lap": earliest_restart["lap"],

                "competitiveLapStartTime": competitive_lap_start,

                "resumeRaceSecond": resume_race_second
            }
        })

    return {
        "redFlags": red_flags
    }

def generate_race_json(
    laps,
    session,
    calendar_date,
    classification_data,
    track_status_df
):
    # Defensive copy
    laps = laps.copy()

    # --- Determine race start time (Lap 1 start) ---
    race_start_time = (
        session.laps
        .loc[session.laps["LapNumber"] == 1, "LapStartTime"]
        .min()
    )

    sector_distance_ratios = compute_sector_distance_ratios(session)
    
    race_control_metadata = build_red_flag_metadata(
        laps,
        track_status_df,
        race_start_time
    )

    race_json = {
        "session": {
            "year": calendar_date.year,
            "Date": f"{calendar_date.month}/{calendar_date.day}",
            "event": session.event["EventName"],
            "location": session.event["Location"],
            "type": "Race",
            "totalLaps": session.total_laps,
            "localTimeAtRaceStart": get_local_race_start_time_str(
                session, calendar_date.year
            ),
            "sectorDistanceRatios": sector_distance_ratios,
        },
        "results": classification_data,
        "raceControl": race_control_metadata,
        "drivers": {}
    }

    for (driver, driver_number), df in laps.groupby(["Driver", "DriverNumber"]):
        df = df.where(df.notna(), None).sort_values("LapNumber")

        driver_block = {
            "driverNumber": driver_number,
            "team": df.iloc[0]["Team"],
            "timing": {
                "laps": [],
                "pitStops": []
            },
            "personalBestLaps": []
        }

        # -------- Lap-1 pit baseline tracking --------
        has_lap1_pit_entry = False
        lap1_start_time = None
        lap1_compound = None

        for _, row in df.iterrows():
            lap_number = int(row["LapNumber"])

            # -------- TIMING → LAPS --------
            driver_block["timing"]["laps"].append({
                "lap": lap_number,
                "lapStartTime": _normalize_timestamp(
                    _to_timedelta_safe(row.get("LapStartTime")),
                    race_start_time
                ),
                "lapTime": _duration_seconds(
                    _to_timedelta_safe(row.get("LapTime"))
                ),
                "sectorTimes": [
                    _duration_seconds(_to_timedelta_safe(row.get("Sector1Time"))),
                    _duration_seconds(_to_timedelta_safe(row.get("Sector2Time"))),
                    _duration_seconds(_to_timedelta_safe(row.get("Sector3Time"))),
                ],
                "positionAtLapEnd": _safe_int(row.get("Position")),
                "tyreLife": _safe_int(row.get("TyreLife")),
            })

            # Capture Lap 1 baseline data
            if lap_number == 1:
                lap1_start_time = _normalize_timestamp(
                    _to_timedelta_safe(row.get("LapStartTime")),
                    race_start_time
                )
                lap1_compound = row.get("Compound")

            # -------- TIMING → PIT STOPS --------
            pit_in = _to_timedelta_safe(row.get("PitInTime"))
            pit_out = _to_timedelta_safe(row.get("PitOutTime"))

            if pit_in is not None or pit_out is not None:
                if lap_number == 1:
                    has_lap1_pit_entry = True

                driver_block["timing"]["pitStops"].append({
                    "lap": lap_number,
                    "pitInTime": _normalize_timestamp(pit_in, race_start_time),
                    "pitOutTime": _normalize_timestamp(pit_out, race_start_time),
                    "compound": row.get("Compound")
                })

            # -------- PERSONAL BEST --------
            if row.get("IsPersonalBest") is True:
                driver_block["personalBestLaps"].append(lap_number)

        # -------- ENSURE LAP 1 PIT ENTRY FOR ALL DRIVERS --------
        if not has_lap1_pit_entry and lap1_start_time is not None:
            driver_block["timing"]["pitStops"].insert(0, {
                "lap": 1,
                "pitInTime": None,
                "pitOutTime": lap1_start_time,
                "compound": lap1_compound
            })

        race_json["drivers"][driver] = driver_block

    return race_json
