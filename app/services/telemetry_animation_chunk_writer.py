from collections import defaultdict

from app.services.telemetry_animation_service import build_driver_telemetry_chunks
from app.services.track_metrics_service import build_track_metrics


def generate_race_telemetry(session):
    """
    Generates race telemetry snapshots in memory.

    Returns:
        dict[int raceSecond -> dict]
        {
          0: { "raceTime": 0, "cars": [...] },
          1: { "raceTime": 1, "cars": [...] },
          ...
        }
    """

    drivers = sorted(session.laps["Driver"].unique())
    track_metrics = build_track_metrics(session)

    # second -> list of driver snapshots
    all_chunks = defaultdict(list)
    
    # global FIA-style timing events
    all_timing_events = []

    drivers = session.laps["Driver"].unique()

    for driver in drivers:
        print(f"▶ Processing telemetry for driver {driver}")

        # driver_data contains:
        # {
        #   "chunks": ...,
        #   "timingEvents": ...
        # }
        driver_data = build_driver_telemetry_chunks(
            session=session,
            driver_code=driver,
            track_metrics=track_metrics,
        )

        driver_chunks = driver_data["chunks"]
        driver_timing_events = driver_data["timingEvents"]
        
        all_timing_events.extend(driver_timing_events)

        for second, snapshot in driver_chunks.items():
            all_chunks[second].append(snapshot)
            
    # --------------------------------------------------
    # GLOBAL FIA TIMING EVENT STREAM
    # --------------------------------------------------
    all_timing_events.sort(
        key=lambda e: e["raceTime"]
    )

    # Build final payloads
    telemetry_json = {}

    for second in sorted(all_chunks.keys()):
        cars = all_chunks[second]

        # 🔒 Safety: ignore empty frames
        if not cars:
            continue

        telemetry_json[int(second)] = {
            "raceTime": int(second),
            "cars": sorted(cars, key=lambda c: c["driver"])
        }


    return {
        "frames": telemetry_json,
        "timingEvents": all_timing_events
    }
