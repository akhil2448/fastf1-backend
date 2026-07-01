from time import perf_counter

from app.services.session_cache_service import get_loaded_session

from app.services.race_management.race_timeline_service import (
    RaceTimelineService,
)

from app.services.race_management.race_progress_collection_service import (
    RaceProgressCollectionService,
)

from app.services.race_management.traffic_index_builder import (
    TrafficIndexBuilder,
)

YEAR = 2024
ROUND = 11
DRIVER = "44"

##############################################################

session = get_loaded_session(
    YEAR,
    ROUND,
)

timeline = (
    RaceTimelineService()
    .build(session)
)

collection = (
    RaceProgressCollectionService()
    .build(session)
)

builder = TrafficIndexBuilder()

##############################################################
# Measure execution time
##############################################################

start = perf_counter()

traffic = builder.build(
    timeline,
    collection,
    DRIVER,
)

elapsed = perf_counter() - start

##############################################################

print()

print("=" * 70)
print("TRAFFIC INDEX")
print("=" * 70)

print()

print("Driver :", traffic.driver_number)

print("Samples:", len(traffic.samples))

print(f"Time   : {elapsed:.3f} seconds")

print()

##############################################################
# Uncomment this block if you want to inspect results
##############################################################

"""
for sample in traffic.samples[:20]:

    ahead = (
        sample.nearest_ahead.driver_number
        if sample.nearest_ahead
        else "-"
    )

    ahead_gap = (
        f"{sample.nearest_ahead.gap_progress:.4f}"
        if sample.nearest_ahead
        else "-"
    )

    behind = (
        sample.nearest_behind.driver_number
        if sample.nearest_behind
        else "-"
    )

    behind_gap = (
        f"{sample.nearest_behind.gap_progress:.4f}"
        if sample.nearest_behind
        else "-"
    )

    print(

        f"Lap {sample.lap_number:2d} | "

        f"{sample.normalized_progress:.3f} | "

        f"Ahead: {ahead:>3} ({ahead_gap}) | "

        f"Behind: {behind:>3} ({behind_gap})"

    )
"""