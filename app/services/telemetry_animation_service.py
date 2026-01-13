import pandas as pd

from app.utils.time_utils import convert_all_timedelta_columns


def build_driver_telemetry_chunks(
    session,
    driver_code,
    sample_rate_ms=200
):
    """
    Builds per-second telemetry snapshots for ONE driver.
    Returns: dict[int raceSecond -> telemetry snapshot]
    """

    # --- Get lap timing data ---
    laps = (
        session.laps
        .pick_drivers([driver_code])[
            ["LapNumber", "LapStartTime", "Time"]
        ]
        .rename(columns={"Time": "LapEndTime"})
        .copy()
    )

    laps = convert_all_timedelta_columns(laps)

    # --- Determine race start time (Lap 1 start) ---
    race_start_time = (
        session.laps
        .loc[session.laps["LapNumber"] == 1, "LapStartTime"]
        .min()
    )

    race_start_seconds = race_start_time.total_seconds()

    # --- Load telemetry ---
    telemetry = (
        session.laps
        .pick_drivers([driver_code])
        .get_telemetry()
        .copy()
    )

    # Only fields needed for animation + ordering
    NUMERIC_COLS = ["Distance", "X", "Y"]
    BASE_COLS = ["SessionTime"] + NUMERIC_COLS

    telemetry = telemetry[[c for c in BASE_COLS if c in telemetry.columns]]
    telemetry = convert_all_timedelta_columns(telemetry)

    # --- Attach LapNumber using timing windows ---
    telemetry["LapNumber"] = None

    for _, lap in laps.iterrows():
        mask = (
            (telemetry["SessionTime"] >= lap["LapStartTime"]) &
            (telemetry["SessionTime"] < lap["LapEndTime"])
        )
        telemetry.loc[mask, "LapNumber"] = lap["LapNumber"]

    telemetry = telemetry.dropna(subset=["LapNumber"])

    # --- Resample at 200 ms ---
    telemetry = telemetry.set_index(pd.to_timedelta(telemetry["SessionTime"]))

    resampled = (
        telemetry[NUMERIC_COLS + ["LapNumber"]]
        .resample(f"{sample_rate_ms}ms")
        .last()
        .infer_objects(copy=False)   # 🔑 FIX
        .interpolate(method="linear")
        .reset_index()
)

    # Fix LapNumber dtype
    resampled["LapNumber"] = (
        resampled["LapNumber"]
        .infer_objects(copy=False)
        .ffill()
        .astype(int)
    )

    # --- Compute race-relative time ---
    resampled["RaceTime"] = (
        resampled["SessionTime"].dt.total_seconds()
        - race_start_seconds
    )

    resampled = resampled[resampled["RaceTime"] >= 0]

    # Bucket into race seconds
    resampled["RaceSecond"] = resampled["RaceTime"].astype(int)

    # 🔑 Take the LAST telemetry point in each race second
    resampled = (
        resampled
        .sort_values("RaceTime")
        .groupby("RaceSecond", as_index=False)
        .tail(1)
    )

    # --- Build chunks ---
    chunks = {}

    for _, row in resampled.iterrows():
        second = int(row["RaceSecond"])

        chunks[second] = {
            "driver": driver_code,
            "lap": int(row["LapNumber"]),
            "distance": float(row["Distance"]),
            "x": float(row["X"]),
            "y": float(row["Y"]),
        }

    return chunks
