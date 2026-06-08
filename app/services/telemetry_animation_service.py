import pandas as pd
import numpy as np
from app.utils.time_utils import convert_all_timedelta_columns


def build_driver_telemetry_chunks(
    session,
    driver_code,
    track_metrics,
    sample_rate_ms=100
):
    """
    Builds per-second telemetry snapshots for ONE driver.
    Returns: dict[int raceSecond -> telemetry snapshot]
    """

    # --------------------------------------------------
    # LAP TIMING DATA
    # --------------------------------------------------
    laps = (
        session.laps
        .pick_drivers([driver_code])[
            ["LapNumber", "LapStartTime", "Time"]
        ]
        .rename(columns={"Time": "LapEndTime"})
        .copy()
    )

    laps = convert_all_timedelta_columns(laps)

    # --------------------------------------------------
    # RACE START TIME (Lap 1 start)
    # --------------------------------------------------
    race_start_time = (
        session.laps
        .loc[session.laps["LapNumber"] == 1, "LapStartTime"]
        .min()
    )

    race_start_seconds = race_start_time.total_seconds()

    # --------------------------------------------------
    # RAW TELEMETRY
    # --------------------------------------------------
    telemetry = (
        session.laps
        .pick_drivers([driver_code])
        .get_telemetry()
        .copy()
    )

    # FastF1 cumulative distance (never resets)
    telemetry = telemetry.add_distance()
    telemetry = convert_all_timedelta_columns(telemetry)

    # --------------------------------------------------
    # ATTACH LAP NUMBER USING TIMING WINDOWS
    # --------------------------------------------------
    telemetry["LapNumber"] = None

    for _, lap in laps.iterrows():
        mask = (
            (telemetry["SessionTime"] >= lap["LapStartTime"]) &
            (telemetry["SessionTime"] < lap["LapEndTime"])
        )
        telemetry.loc[mask, "LapNumber"] = lap["LapNumber"]

    telemetry = telemetry.dropna(subset=["LapNumber"]).copy()
    telemetry["LapNumber"] = telemetry["LapNumber"].astype(int)

    # --------------------------------------------------
    # RESAMPLE (200 ms)
    # --------------------------------------------------
    telemetry = telemetry.set_index(pd.to_timedelta(telemetry["SessionTime"]))

    resampled = (
        telemetry[["Distance", "X", "Y", "LapNumber"]]
        .resample(f"{sample_rate_ms}ms")
        .last()
        .infer_objects(copy=False)
        .interpolate(method="linear")
        .reset_index()
    )

    # Fix LapNumber AFTER resample
    resampled["LapNumber"] = (
        resampled["LapNumber"]
        .ffill()
        .astype(int)
    )

    # --------------------------------------------------
    # LAP DISTANCE (RESET PER LAP)
    # --------------------------------------------------
    resampled["LapDistance"] = (
        resampled["Distance"]
        - resampled.groupby("LapNumber")["Distance"].transform("min")
    )

    # --------------------------------------------------
    # CANONICAL TRACK LENGTH
    # --------------------------------------------------
    track_length = track_metrics["trackLength"]

    timing_loop_count = (
        track_metrics["timingLoopCount"]
    )

    # --------------------------------------------------
    # NORMALIZED TRACK POSITION (0.0 → 1.0)
    # --------------------------------------------------
    resampled["TrackPosition"] = (
        resampled["LapDistance"] / track_length
    ).clip(0.0, 0.999999)

    resampled["TimingLoopIndex"] = (
        np.floor(
            resampled["TrackPosition"] * timing_loop_count
        )
        .astype(int)
        .clip(0, timing_loop_count - 1)
    )
    
    # --------------------------------------------------
    # RACE DISTANCE (MONOTONIC, NEVER RESETS) ✅
    # --------------------------------------------------
    resampled["RaceDistance"] = (
        (resampled["LapNumber"] - 1) * track_length
        + resampled["LapDistance"]
    )

    # --------------------------------------------------
    # RACE-RELATIVE TIME
    # --------------------------------------------------
    resampled["RaceTime"] = (
        resampled["SessionTime"].dt.total_seconds()
        - race_start_seconds
    )

    resampled = resampled[resampled["RaceTime"] >= 0]

    # Bucket into integer race seconds
    resampled["RaceSecond"] = resampled["RaceTime"].astype(int)

    # --------------------------------------------------
    # DETECT TIMING LOOP CROSSINGS
    # --------------------------------------------------
    resampled["PreviousLoopIndex"] = (
        resampled["TimingLoopIndex"].shift(1)
    )

    resampled["PreviousLap"] = (
        resampled["LapNumber"].shift(1)
    )

    resampled["LoopChanged"] = (
        (
            resampled["TimingLoopIndex"]
            != resampled["PreviousLoopIndex"]
        )
        |
        (
            resampled["LapNumber"]
            != resampled["PreviousLap"]
        )
    )

    # Always treat first telemetry point as crossing
    resampled.loc[resampled.index[0], "LoopChanged"] = True

    # --------------------------------------------------
    # BUILD TIMING LOOP EVENTS
    # --------------------------------------------------
    timing_events = []

    loop_crossings = resampled[
        resampled["LoopChanged"]
    ]

    for _, row in loop_crossings.iterrows():
        timing_events.append({
            "driver": driver_code,
            "lap": int(row["LapNumber"]),
            "timingLoopIndex": int(row["TimingLoopIndex"]),
            "raceTime": round(float(row["RaceTime"]), 3),
            "raceDistance": round(float(row["RaceDistance"]),3)
        })

    # --------------------------------------------------
    # ONE SNAPSHOT PER SECOND
    # --------------------------------------------------
    resampled = resampled.sort_values("RaceTime")

    snapshots = []
    for second, group in resampled.groupby("RaceSecond"):
        snapshots.append(group.iloc[0] if second == 0 else group.iloc[-1])

    resampled = pd.DataFrame(snapshots)

    # --------------------------------------------------
    # BUILD FINAL CHUNKS
    # --------------------------------------------------
    chunks = {}

    for _, row in resampled.iterrows():
        second = int(row["RaceSecond"])

        chunks[second] = {
            "driver": driver_code,
            "lap": int(row["LapNumber"]),
            "lapDistance": float(row["LapDistance"]),
            "raceDistance": float(row["RaceDistance"]),
            "trackPosition": float(row["TrackPosition"]),
            "timingLoopIndex": int(row["TimingLoopIndex"]),
            "x": float(row["X"]),
            "y": float(row["Y"]),
        }

    return {
        "chunks": chunks,
        "timingEvents": timing_events
    }
