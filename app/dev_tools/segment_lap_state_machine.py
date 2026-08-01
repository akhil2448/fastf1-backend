from pathlib import Path

import fastf1
import pandas as pd

# from app.services.telemetry_state_machine import (
#     TelemetryStateMachine,
# )


YEAR = 2024
ROUND = 10
SESSION = "R"

DRIVER = "VER"
LAP_NUMBER = 11


def print_summary(segments):

    print()
    print("=" * 80)
    print("SEGMENTS")
    print("=" * 80)

    total = 0

    for segment in segments:

        total += segment.duration

        print(
            f"{segment.state.value:<16}"
            f"{segment.duration:6.2f}s   "
            f"{segment.distance:7.1f}m"
        )

    print()
    print(f"Total analysed time : {total:.3f}s")


def build_summary(segments):

    rows = []

    total = sum(s.duration for s in segments)

    grouped = {}

    for segment in segments:

        grouped.setdefault(segment.state.value, 0)

        grouped[segment.state.value] += segment.duration

    for state, duration in grouped.items():

        rows.append(
            {
                "State": state,
                "DurationSeconds": duration,
                "PercentLap":
                    duration / total * 100,
            }
        )

    return pd.DataFrame(rows)


def export_excel(
    telemetry,
    segments,
):

    segment_rows = []

    for i, segment in enumerate(segments):

        segment_rows.append(
            {
                "Segment": i + 1,
                "State": segment.state.value,
                "StartIndex": segment.start_index,
                "EndIndex": segment.end_index,
                "StartTime": segment.start_time,
                "EndTime": segment.end_time,
                "Duration": segment.duration,
                "StartDistance": segment.start_distance,
                "EndDistance": segment.end_distance,
                "Distance": segment.distance,
            }
        )

    summary = build_summary(segments)

    output = Path(
        f"{DRIVER}_lap_{LAP_NUMBER}_segments.xlsx"
    )

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:

        telemetry.to_excel(
            writer,
            sheet_name="Telemetry",
            index=False,
        )

        pd.DataFrame(segment_rows).to_excel(
            writer,
            sheet_name="Segments",
            index=False,
        )

        summary.to_excel(
            writer,
            sheet_name="Summary",
            index=False,
        )

    print()
    print(f"Exported: {output.resolve()}")


def main():

    fastf1.Cache.enable_cache("cache")

    print()
    print("=" * 80)
    print("Loading session...")
    print("=" * 80)

    session = fastf1.get_session(
        YEAR,
        ROUND,
        SESSION,
    )

    session.load()

    lap = (
        session.laps
        .pick_drivers(DRIVER)
        .pick_laps(LAP_NUMBER)
        .iloc[0]
    )

    telemetry = (
        lap
        .get_car_data()
        .add_distance()
    )

    print()
    print("=" * 80)
    print(f"{DRIVER} Lap {LAP_NUMBER}")
    print("=" * 80)

    print(f"Lap Time : {lap['LapTime']}")
    print(f"Compound : {lap['Compound']}")
    print(f"TyreLife : {lap['TyreLife']}")
    print(f"Stint    : {lap['Stint']}")

    # machine = TelemetryStateMachine()

    # segments, telemetry = machine.analyze(
    #     telemetry
    # )

    # print_summary(segments)

    # export_excel(
    #     telemetry,
    #     segments,
    # )


if __name__ == "__main__":
    main()