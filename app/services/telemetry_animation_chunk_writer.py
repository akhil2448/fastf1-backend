from collections import defaultdict

from app.services.telemetry_animation_service import build_driver_telemetry_chunks


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

    # second -> list of driver snapshots
    all_chunks = defaultdict(list)

    drivers = session.laps["Driver"].unique()

    for driver in drivers:
        print(f"▶ Processing telemetry for driver {driver}")

        # driver_chunks: dict[int raceSecond -> snapshot dict]
        driver_chunks = build_driver_telemetry_chunks(
            session=session,
            driver_code=driver
        )

        for second, snapshot in driver_chunks.items():
            all_chunks[second].append(snapshot)

    # Build final payloads
    telemetry_json = {}

    for second, cars in sorted(all_chunks.items()):
        telemetry_json[int(second)] = {
            "raceTime": int(second),
            "cars": cars
        }

    return telemetry_json
