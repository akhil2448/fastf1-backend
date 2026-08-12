# app/dev_tools/inspect_track_status_mapping.py

from __future__ import annotations

import fastf1
import pandas as pd

from app.services.race_management.race_analyzer.race_metadata_builder import (
    RaceMetadataBuilder,
)

CACHE_DIR = "cache"

YEAR = 2021
ROUND = 21
SESSION = "R"

REFERENCE_DRIVER = "VER"


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

    reference_laps = (
        session.laps
        .pick_drivers(REFERENCE_DRIVER)
        .copy()
    )

    status_names = {
        1: "GREEN",
        2: "YELLOW",
        4: "SAFETY_CAR",
        5: "RED_FLAG",
        6: "VSC",
        7: "VSC_END",
    }

    print()
    print("=" * 120)
    print(f"{YEAR} Round {ROUND} ({SESSION})")
    print(f"Reference Driver: {REFERENCE_DRIVER}")
    print("=" * 120)
    print()

    for _, lap in reference_laps.iterrows():

        lap_number = int(lap["LapNumber"])
        lap_start = lap["LapStartTime"]
        lap_end = lap["Time"]

        print(
            f"\nLap {lap_number:>2}"
            f"    Start={fmt(lap_start)}"
            f"    End={fmt(lap_end)}"
        )

        events = session.track_status[
            (session.track_status["Time"] >= lap_start)
            & (session.track_status["Time"] <= lap_end)
        ]

        if events.empty:
            print("    (no track status events)")
            continue

        for _, event in events.iterrows():

            status = int(event["Status"])

            print(
                f"    {fmt(event['Time'])}"
                f"   {status_names.get(status, status):<12}"
                f"   {event['Message']}"
            )

    print()
    print("=" * 120)
    print("Mapped Incidents")
    print("=" * 120)

    incidents = RaceMetadataBuilder._build_status_ranges(
        session=session,
        reference_laps=reference_laps,
    )

    print()

    for incident in incidents:
        print(incident)


if __name__ == "__main__":
    main()