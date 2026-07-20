from app.services.session_cache_service import get_loaded_session

from app.services.race_management.race_timeline_service import (
    RaceTimelineService,
)

YEAR = 2024
ROUND = 11
DRIVER = "44"

session = get_loaded_session(
    YEAR,
    ROUND,
)

timeline = (
    RaceTimelineService()
    .build(session)
)

driver = timeline.drivers[DRIVER]

print()

print("=" * 70)
print("RACE TIMELINE")
print("=" * 70)

print()

print("Driver:", DRIVER)

print()

for lap in driver.laps[:10]:

    print(

        f"Lap {lap.lap_number:2d} | "

        f"Start {lap.lap_start_time} | "

        f"End {lap.lap_end_time} | "

        f"Lap {lap.lap_time} | "

        f"Cumulative {lap.cumulative_time}"

    )