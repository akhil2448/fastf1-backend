import pandas as pd
import numpy as np
from app.utils.time_utils import convert_all_timedelta_columns

from time import perf_counter


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
    
    total_start = perf_counter()

    timings = {}

    # --------------------------------------------------
    # LAP TIMING DATA
    # --------------------------------------------------
    stage_start = perf_counter()

    laps = (
        session.laps
        .pick_drivers([driver_code])[
            ["LapNumber", "LapStartTime", "Time"]
        ]
        .rename(columns={"Time": "LapEndTime"})
        .copy()
    )

    laps = convert_all_timedelta_columns(laps)

    timings["lap_preparation"] = (
        perf_counter() - stage_start
    )

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
    stage_start = perf_counter()

    telemetry = (
        session.laps
        .pick_drivers([driver_code])
        .get_telemetry()
        .copy()
    )

    timings["get_telemetry"] = (
        perf_counter() - stage_start
    )

    # FastF1 cumulative distance (never resets)
    stage_start = perf_counter()

    telemetry = telemetry.add_distance()

    timings["add_distance"] = (
        perf_counter() - stage_start
    )

    stage_start = perf_counter()

    telemetry = convert_all_timedelta_columns(
        telemetry
    )

    timings["telemetry_conversion"] = (
        perf_counter() - stage_start
    )

    # --------------------------------------------------
    # ATTACH LAP NUMBER USING TIMING WINDOWS
    # --------------------------------------------------
    #
    # For each telemetry sample, find the last lap whose
    # start time is <= the telemetry timestamp, then
    # verify that the timestamp is still before that
    # lap's end time.
    #
    # This preserves the original rule:
    #
    #     SessionTime >= LapStartTime
    #     SessionTime <  LapEndTime
    #
    # while avoiding a full telemetry scan for every lap.
    # --------------------------------------------------

    stage_start = perf_counter()
    
    lap_starts = (
        pd.to_timedelta(
            laps["LapStartTime"]
        )
        .astype("int64")
        .to_numpy()
    )

    lap_ends = (
        pd.to_timedelta(
            laps["LapEndTime"]
        )
        .astype("int64")
        .to_numpy()
    )

    lap_numbers = (
        laps["LapNumber"]
        .to_numpy()
    )

    session_times = (
        pd.to_timedelta(
            telemetry["SessionTime"]
        )
        .astype("int64")
        .to_numpy()
    )

    #
    # Find the last lap whose start time is <=
    # each telemetry sample.
    #
    lap_indexes = (
        np.searchsorted(
            lap_starts,
            session_times,
            side="right",
        )
        - 1
    )

    #
    # Samples before the first lap are invalid.
    #
    valid = (
        lap_indexes >= 0
    )

    #
    # Avoid negative indexing when checking lap ends.
    #
    safe_indexes = np.where(
        valid,
        lap_indexes,
        0,
    )

    #
    # Preserve the original strict end boundary:
    #
    # SessionTime < LapEndTime
    #
    valid &= (
        session_times
        < lap_ends[safe_indexes]
    )

    #
    # Assign lap numbers.
    #
    assigned_laps = np.full(
        len(telemetry),
        np.nan,
    )

    assigned_laps[valid] = (
        lap_numbers[
            lap_indexes[valid]
        ]
    )

    telemetry["LapNumber"] = (
        assigned_laps
    )

    #
    # Remove telemetry that does not belong
    # to any valid lap.
    #
    telemetry = (
        telemetry
        .dropna(
            subset=["LapNumber"]
        )
        .copy()
    )

    telemetry["LapNumber"] = (
        telemetry["LapNumber"]
        .astype(int)
    )
    
    timings["lap_assignment"] = (
        perf_counter() - stage_start
    )

    # --------------------------------------------------
    # RESAMPLE (200 ms)
    # --------------------------------------------------
    stage_start = perf_counter()

    telemetry = telemetry.set_index(
        pd.to_timedelta(
            telemetry["SessionTime"]
        )
    )

    resampled = (
        telemetry[["Distance", "X", "Y", "LapNumber"]]
        .resample(f"{sample_rate_ms}ms")
        .last()
        .infer_objects(copy=False)
        .interpolate(method="linear")
        .reset_index()
    )

    timings["resample_interpolate"] = (
        perf_counter() - stage_start
    )

    # Fix LapNumber AFTER resample
    resampled["LapNumber"] = (
        resampled["LapNumber"]
        .ffill()
        .astype(int)
    )
    
    stage_start = perf_counter()

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
    
    timings["position_calculations"] = (
        perf_counter() - stage_start
    )
    
    stage_start = perf_counter()

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
    
    timings["race_time_bucketing"] = (
        perf_counter() - stage_start
    )

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
    stage_start = perf_counter()

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
    
    timings["timing_events"] = (
        perf_counter() - stage_start
    )

    # --------------------------------------------------
    # ONE SNAPSHOT PER SECOND
    # --------------------------------------------------
    #
    # Preserve the existing selection rule:
    #
    #   RaceSecond == 0  -> first sample
    #   other seconds    -> last sample
    #
    # Since RaceTime is sorted, the first/last occurrence
    # of each RaceSecond can be selected vectorially without
    # a Python groupby loop.
    # --------------------------------------------------

    resampled = resampled.sort_values(
        "RaceTime"
    )

    stage_start = perf_counter()

    first_in_second = (
        ~resampled["RaceSecond"]
        .duplicated(
            keep="first"
        )
    )

    last_in_second = (
        ~resampled["RaceSecond"]
        .duplicated(
            keep="last"
        )
    )

    first_second_zero = (
        (resampled["RaceSecond"] == 0)
        & first_in_second
    )

    last_nonzero_second = (
        (resampled["RaceSecond"] != 0)
        & last_in_second
    )

    selected = (
        first_second_zero
        | last_nonzero_second
    )

    resampled = (
        resampled.loc[selected]
        .copy()
    )

    timings["snapshot_selection"] = (
        perf_counter() - stage_start
    )

    # --------------------------------------------------
    # BUILD FINAL CHUNKS
    # --------------------------------------------------
    stage_start = perf_counter()

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
        
    timings["chunk_construction"] = (
        perf_counter() - stage_start
    )

    total_time = (
        perf_counter() - total_start
    )

    print(
        f"[TELEMETRY] {driver_code} "
        f"total={total_time:.3f}s "
        f"lap_prep={timings.get('lap_preparation', 0.0):.3f}s "
        f"get={timings.get('get_telemetry', 0.0):.3f}s "
        f"distance={timings.get('add_distance', 0.0):.3f}s "
        f"convert={timings.get('telemetry_conversion', 0.0):.3f}s "
        f"lap_assign={timings.get('lap_assignment', 0.0):.3f}s "
        f"resample={timings.get('resample_interpolate', 0.0):.3f}s "
        f"calc={timings.get('position_calculations', 0.0):.3f}s "
        f"time={timings.get('race_time_bucketing', 0.0):.3f}s "
        f"events={timings.get('timing_events', 0.0):.3f}s "
        f"snapshots={timings.get('snapshot_selection', 0.0):.3f}s "
        f"chunks={timings.get('chunk_construction', 0.0):.3f}s"
    )

    return {
        "chunks": chunks,
        "timingEvents": timing_events
    }
