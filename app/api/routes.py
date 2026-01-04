from fastapi import APIRouter
import fastf1

from app.services.session_data_service import load_race_laps_and_weather
from app.services.race_service import generate_race_json
from app.services.circuit_service import generate_track_map
from app.services.year_schedule_service import generate_year_schedule

router = APIRouter()

@router.get("/schedule/{year}")
def get_year_schedule(year: int):
    """
    Returns the full F1 event schedule for a given year.
    """
    return generate_year_schedule(year)

@router.get("/race/{year}/{round}")
def get_race(year: int, round: int):
    session = fastf1.get_session(year, round, "R")

    laps_df = load_race_laps_and_weather(session)
    calendar_date = session.event["EventDate"].date()

    return generate_race_json(laps_df, session, calendar_date)


@router.get("/track-map/{year}/{round}")
def get_track_map(year: int, round: int):
    session = fastf1.get_session(year, round, "R")
    return generate_track_map(session)
