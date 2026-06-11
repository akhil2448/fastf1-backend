import pandas as pd
from app.services.compute_sector_distances import compute_sector_distance_ratios
from app.utils.race_time_utils import get_local_race_start_time_str


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


def generate_race_json(laps, session, calendar_date, classification_data,):
    # Defensive copy
    laps = laps.copy()

    # --- Determine race start time (Lap 1 start) ---
    race_start_time = (
        session.laps
        .loc[session.laps["LapNumber"] == 1, "LapStartTime"]
        .min()
    )

    sector_distance_ratios = compute_sector_distance_ratios(session)

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
