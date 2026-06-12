import re

import pandas as pd


def normalize_category(category):
    """
    Convert camel case categories into spaced words.

    Example:
        CarEvent -> Car Event
        SafetyCar -> Safety Car
    """

    if category is None or pd.isna(category):
        return None

    return re.sub(
        r"(?<!^)([A-Z])",
        r" \1",
        str(category),
    ).strip()


def build_race_control_json(
    session,
    calendar_date
):
    """
    Build normalized race control messages JSON.

    All timestamps are converted into:
        raceSecond

    where:
        raceSecond = 0
    equals:
        actual race start (first Lap 1 start)
    """

    messages = session.race_control_messages

    print(session.race_control_messages.head())
    print(len(session.race_control_messages))

    # ----------------------------------------
    # Determine REAL race start UTC timestamp
    # ----------------------------------------
    race_start_utc = (
        session.laps
        .loc[
            session.laps["LapNumber"] == 1,
            "LapStartDate",
        ]
        .min()
    )

    race_control_json = {
        "session": {
            "year": calendar_date.year,
            "Date": (
                f"{calendar_date.month}/"
                f"{calendar_date.day}"
            ),
            "event": session.event["EventName"],
            "location": session.event["Location"],
            "type": "Race",
        },
        "messages": [],
    }

    # ----------------------------------------
    # Parse race control messages
    # ----------------------------------------
    for index, (_, row) in enumerate(
        messages.iterrows()
    ):

        utc = row.get("Time")

        if utc is None or pd.isna(utc):
            continue

        # ----------------------------------------
        # Convert UTC -> race second
        # ----------------------------------------
        race_second = round(
            (utc - race_start_utc).total_seconds()
        )

        # Ignore pre-race messages
        if race_second < 0:
            continue

        # Ignore blue flags
        if row.get("Flag") == "BLUE":
            continue

        category = normalize_category(
            row.get("Category")
        )

        message_entry = {
            "id": f"{race_second}-{index}",

            "raceSecond": race_second,

            "category": category,

            "message": row.get("Message"),

            "flag": row.get("Flag"),

            "status": row.get("Status"),

            "scope": row.get("Scope"),

            "sector": (
                int(row["Sector"])
                if row.get("Sector") is not None
                and not pd.isna(
                    row.get("Sector")
                )
                else None
            ),

            "racingNumber": (
                row.get("RacingNumber")
            ),

            "lap": (
                int(row["Lap"])
                if row.get("Lap") is not None
                and not pd.isna(row.get("Lap"))
                else None
            ),
        }

        race_control_json["messages"].append(
            message_entry
        )

        # ----------------------------------------
        # Stop after chequered flag
        # ----------------------------------------
        if (
            row.get("Message")
            == "CHEQUERED FLAG"
            and row.get("Flag")
            == "CHEQUERED"
        ):
            break

    return race_control_json