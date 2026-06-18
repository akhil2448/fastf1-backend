import fastf1
import pandas as pd
from datetime import datetime


def _make_json_safe(value):
    if pd.isna(value):
        return None

    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()

    return value


def generate_year_schedule(year: int) -> dict:

    schedule_df = fastf1.get_event_schedule(year)

    schedule_df = schedule_df[
        schedule_df["RoundNumber"] > 0
    ]

    races = []

    for _, row in schedule_df.iterrows():

        race_date = row["Session5Date"]

        if pd.notna(race_date):

            if race_date > datetime.now(race_date.tzinfo):
                continue

        races.append({
            "round": int(row["RoundNumber"]),
            "country": row["Country"],
            "location": row["Location"],
            "officialName": row["OfficialEventName"],
            "raceName": row["EventName"],
            "eventDate": _make_json_safe(row["EventDate"]),

            "qualifyingName": row["Session4"],
            "qualifyingDate": _make_json_safe(row["Session4Date"]),
            "qualifyingDateUtc": _make_json_safe(row["Session4DateUtc"]),

            "raceSessionName": row["Session5"],
            "raceDate": _make_json_safe(row["Session5Date"]),
            "raceDateUtc": _make_json_safe(row["Session5DateUtc"])
        })

    return {
        "year": year,
        "races": races
    }