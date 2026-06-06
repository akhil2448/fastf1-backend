import pandas as pd

def compute_sector_distance_ratios(session):
    """
    Derive sector distance ratios from fastest clean lap.
    """

    session.load(laps=True, telemetry=True)

    # 1️⃣ Pick fastest lap (clean racing line)
    lap = session.laps.pick_fastest()

    s1 = lap["Sector1Time"]
    s2 = lap["Sector2Time"]
    s3 = lap["Sector3Time"]

    if pd.isna(s1) or pd.isna(s2) or pd.isna(s3):
        raise ValueError("Fastest lap has invalid sector times")

    lap_start = lap["LapStartTime"]

    # 2️⃣ Sector end timestamps (session-relative)
    s1_end = lap_start + s1
    s2_end = lap_start + s1 + s2
    s3_end = lap_start + s1 + s2 + s3

    # 3️⃣ Telemetry FROM LAP (✅ correct)
    tel = lap.get_telemetry().copy()
    tel = tel.add_distance()

    tel["sessionSec"] = tel["SessionTime"].dt.total_seconds()

    s1_sec = s1_end.total_seconds()
    s2_sec = s2_end.total_seconds()
    s3_sec = s3_end.total_seconds()

    # 4️⃣ Distances at sector boundaries
    d1 = tel[tel["sessionSec"] <= s1_sec]["Distance"].max()
    d2 = tel[tel["sessionSec"] <= s2_sec]["Distance"].max()
    d3 = tel[tel["sessionSec"] <= s3_sec]["Distance"].max()

    lap_length = d3

    return {
        1: round(d1 / lap_length, 6),
        2: round(d2 / lap_length, 6),
        3: 1.0
    }
