from fastapi import APIRouter
import fastf1
from typing import Optional

from app.services.session_data_service import load_race_laps_and_weather
from app.services.race_service import generate_race_json
from app.services.circuit_service import generate_track_map
from app.services.year_schedule_service import generate_year_schedule
from app.services.weather_service import build_weather_json
from app.services.track_status_service import build_track_status_json
from app.utils.time_utils import convert_all_timedelta_columns
from app.utils.json_utils import sanitize_for_json
from app.services.telemetry_animation_chunk_writer import generate_race_telemetry
from app.services.driver_telemetry_service import get_driver_telemetry

router = APIRouter()

# telemetry_cache[(year, round)] = telemetry_json
telemetry_cache = {}


# -------------------- YEAR SCHEDULE --------------------
@router.get("/schedule/{year}")
def get_year_schedule(year: int):
    """
    Returns the full F1 event schedule for a given year.
    """
    return generate_year_schedule(year)


# -------------------- RACE DATA --------------------
@router.get("/race/{year}/{round}")
def get_race(year: int, round: int):
    session = fastf1.get_session(year, round, "R")

    laps_df = load_race_laps_and_weather(session)
    calendar_date = session.event["EventDate"].date()

    race_json = generate_race_json(laps_df, session, calendar_date)

    return sanitize_for_json(race_json)


# -------------------- WEATHER DATA --------------------
@router.get("/weather/{year}/{round}")
def get_weather(year: int, round: int):
    session = fastf1.get_session(year, round, "R")
    session.load(weather=True)

    weather_df = convert_all_timedelta_columns(session.weather_data)
    calendar_date = session.event["EventDate"].date()

    return build_weather_json(weather_df, session, calendar_date)


# -------------------- TRACK STATUS --------------------
@router.get("/track-status/{year}/{round}")
def get_track_status(year: int, round: int):
    session = fastf1.get_session(year, round, "R")

    laps_df = load_race_laps_and_weather(session)
    track_status_df = convert_all_timedelta_columns(
        laps_df[["Time", "TrackStatus"]]
    )

    calendar_date = session.event["EventDate"].date()

    return build_track_status_json(track_status_df, session, calendar_date)


# -------------------- TRACK MAP --------------------
@router.get("/track-map/{year}/{round}")
def get_track_map(year: int, round: int):
    session = fastf1.get_session(year, round, "R")
    return generate_track_map(session)


# -------------------- RACE TELEMETRY --------------------
@router.get("/telemetry/{year}/{round}")
def get_race_telemetry(
    year: int,
    round: int,
    from_second: int,
    to_second: int
):
    """
    Returns telemetry animation snapshots for a race
    between [from_second, to_second].

    Example:
    /telemetry/2021/7?from_second=1832&to_second=1892
    """

    cache_key = (year, round)

    # --- Load & cache telemetry once ---
    if cache_key not in telemetry_cache:
        session = fastf1.get_session(year, round, "R")

        # IMPORTANT: telemetry animation needs laps only
        session.load(laps=True)

        telemetry_cache[cache_key] = generate_race_telemetry(session)

    telemetry_data = telemetry_cache[cache_key]

    # --- Slice requested window ---
    frames = {
        sec: telemetry_data[sec]
        for sec in range(from_second, to_second + 1)
        if sec in telemetry_data
    }

    return {
        "from": from_second,
        "to": to_second,
        "frames": frames
    }

# -------------------- DRIVER TELEMETRY --------------------
@router.get("/driver-telemetry/{year}/{round}/{driver}")
def get_driver_telemetry_route(
    year: int,
    round: int,
    driver: str,
    from_second: float,
    to_second: float,
    sample_rate_ms: int = 100
):
    """
    Returns high-resolution telemetry for a specific driver
    between race-relative time window.

    Example:
    /driver-telemetry/2021/7/LEC?from_second=1832&to_second=2432&sample_rate_ms=100
    """

    # --- Load session ---
    session = fastf1.get_session(year, round, "R")

    # IMPORTANT: driver telemetry needs telemetry data
    session.load(telemetry=True, laps=True)

    telemetry = get_driver_telemetry(
        session=session,
        driver_code=driver.upper(),
        from_race_second=from_second,
        to_race_second=to_second,
        sample_rate_ms=sample_rate_ms
    )

    return {
        "driver": driver.upper(),
        "from": from_second,
        "to": to_second,
        "sampleRateMs": sample_rate_ms,
        "count": len(telemetry),
        "telemetry": telemetry
    }
