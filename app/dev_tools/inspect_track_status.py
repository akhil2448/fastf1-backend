# app/dev_tools/inspect_track_status.py

from __future__ import annotations

import fastf1
import pandas as pd

CACHE_DIR = "cache"


def main():
    fastf1.Cache.enable_cache(CACHE_DIR)

    year = 2021
    round_number = 21  # Saudi Arabian GP
    session_name = "R"

    session = fastf1.get_session(year, round_number, session_name)
    session.load()

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)

    print("\n========== TRACK STATUS ==========\n")

    print(session.track_status)

    print("\n========== EVENTS ==========\n")

    for index, row in session.track_status.iterrows():
        print(
            f"{index:>3} | "
            f"Time={row['Time']} | "
            f"Status={row['Status']} | "
            f"Message={row.get('Message', '<no message>')}"
        )

    print("\n========== COLUMN INFO ==========\n")
    print(session.track_status.dtypes)


if __name__ == "__main__":
    main()