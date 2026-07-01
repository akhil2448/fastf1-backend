from app.services.session_cache_service import get_loaded_session

from app.services.race_management.race_progress_collection_service import (
    RaceProgressCollectionService,
)

YEAR = 2024
ROUND = 11

session = get_loaded_session(
    YEAR,
    ROUND,
)

service = RaceProgressCollectionService()

collection = service.build(
    session,
)

print()

print("=" * 70)
print("RACE PROGRESS COLLECTION")
print("=" * 70)

print()

print(
    "Drivers:",
    len(collection.drivers),
)

print()

for driver, frame in collection.drivers.items():

    print(
        f"{driver:>3}   "
        f"{len(frame.samples)} samples"
    )