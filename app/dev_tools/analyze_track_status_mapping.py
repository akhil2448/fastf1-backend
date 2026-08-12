from pprint import pprint

import fastf1
import pandas as pd

YEAR = 2021
ROUND = 21
SESSION = "R"
REFERENCE_DRIVER = "VER"


def print_section(title: str):
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


def find_reference_lap(reference_laps: pd.DataFrame, session_time):

    for _, lap in reference_laps.iterrows():

        start = lap["LapStartTime"]
        end = lap["Time"]

        if (
            pd.notna(start)
            and pd.notna(end)
            and start <= session_time <= end
        ):
            return {
                "lap": int(lap["LapNumber"]),
                "lapStart": round(start.total_seconds(), 3),
                "lapEnd": round(end.total_seconds(), 3),
                "lapTime": (
                    round(
                        lap["LapTime"].total_seconds(),
                        3,
                    )
                    if pd.notna(lap["LapTime"])
                    else None
                ),
            }

    return None


def main():

    fastf1.Cache.enable_cache("cache")

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

    print_section(
        f"Reference Driver: {REFERENCE_DRIVER}"
    )

    print(
        reference_laps[
            [
                "LapNumber",
                "LapStartTime",
                "Time",
                "LapTime",
                "TrackStatus",
            ]
        ]
    )

    print_section("Track Status Mapping")

    rows = []

    for _, status in session.track_status.iterrows():

        mapping = find_reference_lap(
            reference_laps,
            status["Time"],
        )

        rows.append(
            {
                "SessionTime": round(
                    status["Time"].total_seconds(),
                    3,
                ),
                "Status": int(status["Status"]),
                "Message": status["Message"],
                "ReferenceLap": (
                    mapping["lap"]
                    if mapping
                    else None
                ),
                "LapStart": (
                    mapping["lapStart"]
                    if mapping
                    else None
                ),
                "LapEnd": (
                    mapping["lapEnd"]
                    if mapping
                    else None
                ),
            }
        )

    df = pd.DataFrame(rows)

    print(df)

    filename = (
        f"track_status_mapping_"
        f"{YEAR}_{ROUND}_{REFERENCE_DRIVER}.xlsx"
    )

    with pd.ExcelWriter(
        filename,
        engine="openpyxl",
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="TrackStatus",
            index=False,
        )

        reference_laps[
            [
                "LapNumber",
                "LapStartTime",
                "Time",
                "LapTime",
                "TrackStatus",
            ]
        ].to_excel(
            writer,
            sheet_name="ReferenceLaps",
            index=False,
        )

    print()
    print(f"Exported: {filename}")


if __name__ == "__main__":
    main()