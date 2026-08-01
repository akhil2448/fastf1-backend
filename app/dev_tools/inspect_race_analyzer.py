"""
Developer utility for inspecting all race data available from FastF1.

Run:

python -m app.dev_tools.inspect_race_analyzer
"""

from pprint import pprint

# from app.services.session_cache_service import SessionCacheService

import fastf1

# session = fastf1.get_session(2024, 10, "R")
# session.load()


YEAR = 2024
ROUND = 10
DRIVER = "VER"


def print_section(title: str):
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


def main():
    # cache = SessionCacheService()

    print("Loading race session...")

    session = session = fastf1.get_session(YEAR, ROUND, "R")
    session.load()

    print(f"Loaded: {session.event['EventName']} ({YEAR})")

    ####################################################################
    # Session
    ####################################################################

    print_section("SESSION INFO")

    print("Name:", session.name)
    print("Event:", session.event["EventName"])
    print("Location:", session.event["Location"])

    ####################################################################
    # Results
    ####################################################################

    print_section("RESULTS COLUMNS")

    print(session.results.columns.tolist())

    ####################################################################
    # Laps dataframe
    ####################################################################

    print_section("LAPS DATAFRAME COLUMNS")

    pprint(session.laps.columns.tolist())

    ####################################################################
    # Driver laps
    ####################################################################

    laps = session.laps.pick_driver(DRIVER)

    print_section(f"{DRIVER} LAP COUNT")

    print(len(laps))

    ####################################################################
    # Sample lap
    ####################################################################

    lap = laps.iloc[10]

    print_section("SAMPLE LAP")

    print(lap)
    
    
    print_section("ALL LAPS SUMMARY")

    summary = laps[
        [
            "LapNumber",
            "LapTime",
            "Sector1Time",
            "Sector2Time",
            "Sector3Time",
            "Compound",
            "TyreLife",
            "Stint",
            "Position",
            "TrackStatus",
            "PitInTime",
            "PitOutTime",
            "Deleted",
            "DeletedReason",
            "FastF1Generated",
        ]
    ]

    print(summary)

    ####################################################################
    # Every lap property
    ####################################################################

    print_section("SAMPLE LAP FIELDS")

    for key in lap.index:
        print(f"{key}: {lap[key]}")

    ####################################################################
    # Car telemetry
    ####################################################################

    car = lap.get_car_data()

    print_section("CAR DATA COLUMNS")

    pprint(car.columns.tolist())

    print_section("CAR DATA SAMPLE")

    print(car.head(20))

    ####################################################################
    # Position telemetry
    ####################################################################

    pos = lap.get_pos_data()

    print_section("POSITION DATA COLUMNS")

    pprint(pos.columns.tolist())

    print_section("POSITION DATA SAMPLE")

    print(pos.head(20))

    ####################################################################
    # Weather
    ####################################################################

    weather = session.weather_data

    print_section("WEATHER COLUMNS")

    pprint(weather.columns.tolist())

    print_section("WEATHER SAMPLE")

    print(weather.head(30))

    ####################################################################
    # Track Status
    ####################################################################

    track = session.track_status

    print_section("TRACK STATUS COLUMNS")

    pprint(track.columns.tolist())

    print_section("TRACK STATUS SAMPLE")

    print(track.head(100))

    ####################################################################
    # Race Control
    ####################################################################

    if hasattr(session, "race_control_messages"):
        messages = session.race_control_messages

        print_section("RACE CONTROL COLUMNS")

        pprint(messages.columns.tolist())

        print_section("RACE CONTROL SAMPLE")

        print(messages.head(100))
    else:
        print_section("RACE CONTROL")

        print("Race Control messages not available.")

    ####################################################################
    # Session Status
    ####################################################################

    if hasattr(session, "session_status"):
        status = session.session_status

        print_section("SESSION STATUS COLUMNS")

        pprint(status.columns.tolist())

        print_section("SESSION STATUS SAMPLE")

        print(status.head(50))

    ####################################################################
    # Driver object
    ####################################################################

    print_section("DRIVER OBJECT")

    pprint(session.get_driver(DRIVER))

    ####################################################################
    # Event metadata
    ####################################################################

    print_section("EVENT")

    pprint(dict(session.event))


if __name__ == "__main__":
    main()