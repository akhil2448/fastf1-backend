from app.services.session_cache_service import get_loaded_session

from app.services.race_management.race_timeline_service import (
    RaceTimelineService,
)

from app.services.race_management.race_timeline_query_service import (
    RaceTimelineQueryService,
)

YEAR = 2024
ROUND = 11

session = get_loaded_session(
    YEAR,
    ROUND,
)

timeline = (
    RaceTimelineService()
    .build(session)
)

query = RaceTimelineQueryService()

##############################################################
# Pick a known time
##############################################################

driver = timeline.drivers["44"]

sample_lap = driver.laps[20]

time = sample_lap.lap_start_time + (
    sample_lap.lap_time / 2
)

print()

print("=" * 70)
print("QUERY")
print("=" * 70)

print()

lap = query.get_driver_lap(
    timeline,
    "44",
    time,
)

print("Driver 44")

print(
    "Session Time:",
    time,
)

print(
    "Current Lap:",
    lap.lap_number,
)

print()

drivers = query.get_drivers_on_lap(
    timeline,
    lap.lap_number,
    time,
)

print(
    "Drivers on same lap:"
)

for driver in drivers:

    print(driver)