import pandas as pd


def get_driver_telemetry(
    session,
    driver_code,
    from_race_second: float,
    to_race_second: float,
    sample_rate_ms=100
):
    """
    Returns high-resolution telemetry for ONE driver
    between race-relative time window.
    """

    # --- Determine race start (Lap 1 start) ---
    race_start_time = (
        session.laps
        .loc[session.laps["LapNumber"] == 1, "LapStartTime"]
        .min()
    )
    race_start_seconds = race_start_time.total_seconds()

    # --- Load telemetry (DO NOT convert timedeltas here) ---
    # telemetry = (
    #     session.laps
    #     .pick_drivers([driver_code])
    #     .get_telemetry()
    #     .copy()
    # )

    # --- Resolve driver number safely ---
    driver_rows = session.laps[session.laps["Driver"] == driver_code]

    if driver_rows.empty:
        return []

    driver_number = driver_rows.iloc[0]["DriverNumber"]

    if pd.isna(driver_number):
        return []

    # --- Load telemetry using explicit driver number ---
    try:
        telemetry = (
            session.car_data[driver_number]
            .copy()
        )
        print("Fetching data for DriverNumber: ", driver_number)
    except KeyError:
        return []

    # --- Compute race-relative time (seconds, float) ---
    telemetry["RaceTime"] = (
        telemetry["SessionTime"].dt.total_seconds()
        - race_start_seconds
    )

    # --- Filter requested window ---
    telemetry = telemetry[
        (telemetry["RaceTime"] >= from_race_second) &
        (telemetry["RaceTime"] <= to_race_second)
    ]

    if telemetry.empty:
        return []

    # --- Keep only required telemetry fields ---
    telemetry = telemetry[[
        "RaceTime",
        "RPM",
        "Speed",
        "nGear",
        "Throttle",
        "Brake"
    ]]

    # --- Resample using race-relative time ---
    telemetry = telemetry.set_index(
        pd.to_timedelta(telemetry["RaceTime"], unit="s")
    )

    telemetry = (
        telemetry
        .resample(f"{sample_rate_ms}ms")
        .last()
        .interpolate(method="linear")
        .reset_index(drop=True)
    )

    # --- Serialize to JSON-safe format ---
    return [
        {
            "t": round(float(row["RaceTime"]), 3),
            "rpm": int(row["RPM"]) if not pd.isna(row["RPM"]) else None,
            "speed": float(row["Speed"]) if not pd.isna(row["Speed"]) else None,
            "gear": int(row["nGear"]) if not pd.isna(row["nGear"]) else None,
            "throttle": float(row["Throttle"]) if not pd.isna(row["Throttle"]) else None,
            "brake": bool(row["Brake"]) if not pd.isna(row["Brake"]) else False
        }
        for _, row in telemetry.iterrows()
    ]
