from pprint import pprint

import fastf1
import pandas as pd

###############################################################################
# Select ONE race to inspect
###############################################################################

# 2024 Spain (Clean race)
# session = fastf1.get_session(2024, 10, "R")

# 2023 Australia (Red Flag + Safety Cars)
# session = fastf1.get_session(2023, 3, "R")

# 2022 Silverstone (Red Flag)
# session = fastf1.get_session(2022, 10, "R")

# 2021 Hungary (Red Flag)
# session = fastf1.get_session(2021, 11, "R")

# 2021 Saudi Arabia (VSC + SC + Red Flag)
session = fastf1.get_session(2021, 21, "R")

# 2021 Azerbaijan (Red Flag)
# session = fastf1.get_session(2021, 6, "R")


def print_section(title: str):
    print("\n")
    print("=" * 100)
    print(title)
    print("=" * 100)


def inspect_dataframe(name: str, df: pd.DataFrame):
    print_section(name)

    print(f"Rows: {len(df)}")
    print()

    print("Columns:")
    print(list(df.columns))

    print()

    print(df.head(50))

    print()


def main():
    fastf1.Cache.enable_cache("cache")
    session.load()

    print_section("EVENT")

    event = session.event

    print(f"Year      : {event['EventDate'].year}")
    print(f"Round     : {event['RoundNumber']}")
    print(f"Event     : {event['EventName']}")
    print(f"Location  : {event['Location']}")
    print(f"Country   : {event['Country']}")
    print(f"TotalLaps : {session.total_laps}")

    #
    # Race Control Messages
    #
    print_section("Race Control Messages")

    messages = session.race_control_messages.copy()

    interesting_flags = [
        "GREEN",
        "YELLOW",
        "RED",
        "SC",
        "VSC",
        "DOUBLE YELLOW",
    ]

    interesting_categories = [
        "Flag",
        "SafetyCar",
    ]

    messages = messages[
        messages["Category"].isin(interesting_categories)
        | messages["Flag"].isin(interesting_flags)
    ]

    print(messages)
    
    print_section("Track Status Codes")

    print(session.track_status["Status"].value_counts().sort_index())
    
    print_section("Track Status Changes")

    interesting = session.track_status[
        session.track_status["Status"] != "1"
    ]

    print(interesting)
    
    print_section("Track Status Timeline")

    for _, row in session.track_status.iterrows():
        print(
            f"{row.Time} | "
            f"Status={row.Status} | "
            f"{row.Message}"
        )

    #
    # Track Status
    #
    inspect_dataframe(
        "Track Status",
        session.track_status,
    )

    #
    # Weather
    #
    inspect_dataframe(
        "Weather",
        session.weather_data,
    )

    #
    # Session Status
    #
    inspect_dataframe(
        "Session Status",
        session.session_status,
    )

    #
    # Driver Laps (sample)
    #
    print_section("VER SAMPLE LAPS")

    laps = (
        session.laps
        .pick_drivers("VER")
        .loc[
            :,
            [
                "LapNumber",
                "LapStartTime",
                "Time",
                "LapTime",
                "Position",
                "Stint",
                "Compound",
                "TyreLife",
                "TrackStatus",
                "IsAccurate",
            ],
        ]
    )

    print(laps.head(30))


if __name__ == "__main__":
    main()