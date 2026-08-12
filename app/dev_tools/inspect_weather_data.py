from __future__ import annotations

import fastf1
import pandas as pd

CACHE_DIR = "cache"

YEAR = 2021
ROUND = 11
SESSION = "R"


def fmt(td):
    if pd.isna(td):
        return "None"
    return f"{td.total_seconds():9.3f}s"


def main():

    fastf1.Cache.enable_cache(CACHE_DIR)

    session = fastf1.get_session(
        YEAR,
        ROUND,
        SESSION,
    )

    session.load()

    weather = session.weather_data

    print()
    print("=" * 120)
    print("WEATHER DATA")
    print("=" * 120)
    print()

    print(weather.head(20))

    print()
    print("=" * 120)
    print("COLUMN TYPES")
    print("=" * 120)
    print(weather.dtypes)

    print()
    print("=" * 120)
    print("RAINFALL EVENTS")
    print("=" * 120)

    rain = weather[weather["Rainfall"] == True]

    if rain.empty:
        print("No rainfall recorded.")
        return

    print()

    for _, row in rain.iterrows():

        print(
            f"{fmt(row['Time'])}"
            f"  Rain={row['Rainfall']}"
            f"  Air={row['AirTemp']}"
            f"  Track={row['TrackTemp']}"
            f"  Humidity={row['Humidity']}"
        )


if __name__ == "__main__":
    main()