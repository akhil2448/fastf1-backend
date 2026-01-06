import fastf1
import json

from app.services.year_schedule_service import generate_year_schedule
from app.services.session_data_service import load_race_laps_and_weather
from app.services.race_service import generate_race_json
from app.services.weather_service import build_weather_json
from app.services.track_status_service import build_track_status_json
from app.services.circuit_service import generate_track_map
from app.dev_tools.circuit_visualizer import visualize_track_map
from app.utils.time_utils import convert_all_timedelta_columns

# Enable cache (once per run)
fastf1.Cache.enable_cache("cache")

YEAR = 2021
ROUND = 7

# Toggle visualization here (DEV ONLY)
VISUALIZE_TRACK = True

def test_year_schedule_generation():
    generate_year_schedule(
        year=2025,
        output_file="out_2025_schedule.json"
    )
    print("✅ schedule.json generated")

def test_race_data_generation():
    session = fastf1.get_session(YEAR, ROUND, "R")
    laps_df = load_race_laps_and_weather(session)

    calendar_date = session.event["EventDate"].date()

    race_json = generate_race_json(
        laps=laps_df,
        session=session,
        calendar_date=calendar_date
    )

    with open("out_race.json", "w") as f:
        json.dump(race_json, f, indent=2)

    print("✅ race.json generated")


def test_weather_data_generation():
    session = fastf1.get_session(YEAR, ROUND, "R")
    session.load(weather=True)

    weather_df = convert_all_timedelta_columns(session.weather_data)
    calendar_date = session.event["EventDate"].date()

    weather_json = build_weather_json(
        weather_df=weather_df,
        session=session,
        calendar_date=calendar_date
    )

    with open("out_weather.json", "w") as f:
        json.dump(weather_json, f, indent=2)

    print("✅ weather.json generated")


def test_track_status_generation():
    session = fastf1.get_session(YEAR, ROUND, "R")
    laps_df = load_race_laps_and_weather(session)

    track_status_df = convert_all_timedelta_columns(
        laps_df[["Time", "TrackStatus"]]
    )

    calendar_date = session.event["EventDate"].date()

    track_status_json = build_track_status_json(
        track_status_df=track_status_df,
        session=session,
        calendar_date=calendar_date
    )

    with open("out_track_status.json", "w") as f:
        json.dump(track_status_json, f, indent=2)

    print("✅ track_status.json generated")


def test_track_map_generation():
    session = fastf1.get_session(YEAR, ROUND, "R")
    track_map = generate_track_map(session)

    with open("out_track_map.json", "w") as f:
        json.dump(track_map, f, indent=2)

    print("✅ track_map.json generated")

    # 🔍 DEV-ONLY visualization
    if VISUALIZE_TRACK:
        visualize_track_map(track_map)


if __name__ == "__main__":
    test_race_data_generation()
    test_weather_data_generation()
    test_track_status_generation()
    test_track_map_generation()
    test_year_schedule_generation()
    

