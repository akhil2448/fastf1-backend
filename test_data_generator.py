import fastf1
import json
import os

from app.services.year_schedule_service import generate_year_schedule
from app.services.session_data_service import load_race_laps_and_weather
from app.services.race_service import generate_race_json
from app.services.weather_service import build_weather_json
from app.services.track_status_service import build_track_status_json
from app.services.circuit_service import generate_track_map
from app.dev_tools.circuit_visualizer import visualize_track_map
from app.utils.time_utils import convert_all_timedelta_columns
from app.services.telemetry_animation_chunk_writer import generate_race_telemetry
from app.services.driver_telemetry_service import get_driver_telemetry

# -----------------------------
# GLOBAL SETUP (ONCE PER RUN)
# -----------------------------

fastf1.Cache.enable_cache("cache")

YEAR = 2020
ROUND = 1
SESSION_TYPE = "R"

VISUALIZE_TRACK = True

# Create ONE session object
SESSION = fastf1.get_session(YEAR, ROUND, SESSION_TYPE)


def ensure_loaded(*, laps=False, telemetry=False, weather=False):
    """
    Safely load required session data incrementally.
    FastF1 will skip already-loaded data automatically.
    """
    SESSION.load(
        laps=laps,
        telemetry=telemetry,
        weather=weather
    )


# -----------------------------
# TEST FUNCTIONS
# -----------------------------

def test_year_schedule_generation():
    schedule = generate_year_schedule(year=2025)

    with open("out_2025_schedule.json", "w") as f:
        json.dump(schedule, f, indent=2)

    print("✅ out_2025_schedule.json generated")


def test_race_data_generation():
    ensure_loaded(laps=True)

    laps_df = load_race_laps_and_weather(SESSION)
    calendar_date = SESSION.event["EventDate"].date()

    race_json = generate_race_json(
        laps=laps_df,
        session=SESSION,
        calendar_date=calendar_date
    )

    with open("out_race.json", "w") as f:
        json.dump(race_json, f, indent=2)

    print("✅ race.json generated")


def test_weather_data_generation():
    ensure_loaded(weather=True)

    weather_df = convert_all_timedelta_columns(SESSION.weather_data)
    calendar_date = SESSION.event["EventDate"].date()

    weather_json = build_weather_json(
        weather_df=weather_df,
        session=SESSION,
        calendar_date=calendar_date
    )

    with open("out_weather.json", "w") as f:
        json.dump(weather_json, f, indent=2)

    print("✅ weather.json generated")


def test_track_status_generation():
    ensure_loaded(laps=True)

    laps_df = load_race_laps_and_weather(SESSION)
    track_status_df = convert_all_timedelta_columns(
        laps_df[["Time", "TrackStatus"]]
    )

    calendar_date = SESSION.event["EventDate"].date()

    track_status_json = build_track_status_json(
        track_status_df=track_status_df,
        session=SESSION,
        calendar_date=calendar_date
    )

    with open("out_track_status.json", "w") as f:
        json.dump(track_status_json, f, indent=2)

    print("✅ track_status.json generated")


def test_track_map_generation():
    ensure_loaded(laps=True)

    track_map = generate_track_map(SESSION)

    with open("out_track_map.json", "w") as f:
        json.dump(track_map, f, indent=2)

    print("✅ track_map.json generated")

    if VISUALIZE_TRACK:
        visualize_track_map(track_map)


def test_telemetry_generation():
    ensure_loaded(laps=True)

    telemetry_data = generate_race_telemetry(session=SESSION)

    output_dir = "out_telemetry"
    os.makedirs(output_dir, exist_ok=True)

    for second, payload in telemetry_data.items():
        with open(f"{output_dir}/{second}.json", "w") as f:
            json.dump(payload, f, indent=2)

    print(f"✅ Telemetry chunks generated: {len(telemetry_data)} seconds")


def test_driver_telemetry_generation():
    """
    High-resolution telemetry buffer for a single driver.
    API-ready structure.
    """

    DRIVER = "VER"
    START_SECOND = 500
    BUFFER_SECONDS = 600   # 10 minutes
    SAMPLE_RATE_MS = 100

    ensure_loaded(laps=True, telemetry=True)

    telemetry_data = get_driver_telemetry(
        session=SESSION,
        driver_code=DRIVER,
        from_race_second=START_SECOND,
        to_race_second=START_SECOND + BUFFER_SECONDS,
        sample_rate_ms=SAMPLE_RATE_MS
    )

    output = {
        "driver": DRIVER,
        "from": START_SECOND,
        "to": START_SECOND + BUFFER_SECONDS,
        "sampleRateMs": SAMPLE_RATE_MS,
        "count": len(telemetry_data),
        "telemetry": telemetry_data
    }

    with open(f"out_driver_telemetry_{DRIVER}.json", "w") as f:
        json.dump(output, f, indent=2)

    print(
        f"✅ Driver telemetry generated for {DRIVER}: "
        f"{len(telemetry_data)} samples"
    )


# -----------------------------
# ENTRY POINT
# -----------------------------

if __name__ == "__main__":
    # Uncomment what you want to test

    ensure_loaded(laps=True, telemetry=True, weather=True)

    # test_year_schedule_generation()
    # test_race_data_generation()
    # test_weather_data_generation()
    # test_track_status_generation()
    # test_track_map_generation()
    test_telemetry_generation()
    #test_driver_telemetry_generation()
