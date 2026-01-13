import fastf1
import pandas as pd
import json
from datetime import datetime


def _make_json_safe(value):
    """
    Converts Pandas/Datetime objects into JSON-serializable values.
    """
    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if isinstance(value, datetime):
        return value.isoformat()

    return value


def generate_year_schedule(
    year: int,
    output_file: str = "year_schedule.json"
) -> dict:
    """
    Fetches the full F1 event schedule for a given year
    and writes it to a JSON file with ALL columns preserved.
    """

    # Fetch schedule
    schedule_df = fastf1.get_event_schedule(year)

    # Convert ALL values to JSON-safe
    schedule_df = schedule_df.applymap(_make_json_safe)

    schedule_json = {
        "year": year,
        "events": schedule_df.to_dict(orient="records")
    }

    return schedule_json
