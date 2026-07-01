from app.services.session_cache_service import (
    get_loaded_session,
)

from app.services.race_management.race_timeline_service import (
    RaceTimelineService,
)

from app.services.race_management.traffic_candidate_service import (
    TrafficCandidateService,
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

ham = timeline.drivers[DRIVER]

lap = ham.laps[20]

time = lap.lap_start_time + (
    lap.lap_time / 2
)

service = TrafficCandidateService()

drivers = service.get_candidates(
    timeline,
    DRIVER,
    time,
)

print()

print("=" * 70)
print("TRAFFIC CANDIDATES")
print("=" * 70)

print()

print("Driver :", DRIVER)
print("Time   :", time)

print()

print("Candidates")

print("-" * 70)

for driver in drivers:

    print(driver)