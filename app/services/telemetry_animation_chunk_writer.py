from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.services.telemetry_animation_service import build_driver_telemetry_chunks
from app.services.track_metrics_service import build_track_metrics

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


def _process_driver(driver, session, track_metrics):

    print(f"▶ Processing telemetry for driver {driver}")

    return build_driver_telemetry_chunks(
        session=session,
        driver_code=driver,
        track_metrics=track_metrics,
    )


def generate_race_telemetry(session):

    drivers = sorted(session.laps["Driver"].unique())

    track_metrics = build_track_metrics(session)

    # second -> list of driver snapshots
    all_chunks = defaultdict(list)

    # global FIA-style timing events
    all_timing_events = []

    # ==================================================
    # PARALLEL DRIVER PROCESSING
    # ==================================================

    with ThreadPoolExecutor(max_workers=6) as executor:

        futures = {
            executor.submit(
                _process_driver,
                driver,
                session,
                track_metrics
            ): driver
            for driver in drivers
        }

        for future in as_completed(futures):

            driver = futures[future]

            try:

                driver_data = future.result()

                driver_chunks = driver_data["chunks"]

                driver_timing_events = driver_data["timingEvents"]

                all_timing_events.extend(driver_timing_events)

                for second, snapshot in driver_chunks.items():
                    all_chunks[second].append(snapshot)

            except Exception as e:

                print(
                    f"❌ Failed processing telemetry "
                    f"for driver {driver}: {e}"
                )

    # --------------------------------------------------
    # GLOBAL FIA TIMING EVENT STREAM
    # --------------------------------------------------

    all_timing_events.sort(
        key=lambda e: e["raceTime"]
    )

    telemetry_json = {}

    for second in sorted(all_chunks.keys()):

        cars = all_chunks[second]

        if not cars:
            continue

        telemetry_json[int(second)] = {
            "raceTime": int(second),
            "cars": sorted(
                cars,
                key=lambda c: c["driver"]
            )
        }

    return {
        "frames": telemetry_json,
        "timingEvents": all_timing_events
    }

