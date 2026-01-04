from fastapi import APIRouter
import fastf1

from app.services.session_data_service import load_race_laps_and_weather
from app.services.race_service import generate_race_json
from app.services.circuit_service import generate_track_map
from app.services.year_schedule_service import generate_year_schedule
from app.services.weather_service import build_weather_json
from app.services.track_status_service import build_track_status_json
from app.utils.time_utils import convert_all_timedelta_columns
from app.utils.json_utils import sanitize_for_json

router = APIRouter()


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
