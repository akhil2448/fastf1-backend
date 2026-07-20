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
LAP = 21

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

traffic_frame = (
    TrafficIndexBuilder()
    .build(
        timeline,
        collection,
        DRIVER,
    )
)

##############################################################

lap_samples = traffic_frame.samples_for_lap(
    LAP,
)

print()

print("=" * 90)
print("TRAFFIC TRACE")
print("=" * 90)

print()

print(
    f"Driver : {DRIVER}"
)

print(
    f"Lap    : {LAP}"
)

print(
    f"Samples: {len(lap_samples)}"
)

print()

print(
    f"{'Session Time':<20}"
    f"{'Ahead':>8}"
    f"{'Gap':>14}"
    f"{'Behind':>10}"
    f"{'Gap':>14}"
)

print("-" * 90)

##############################################################
# Print every 10th telemetry sample
##############################################################

STEP = 10

for sample in lap_samples[::STEP]:

    ahead = "-"

    ahead_gap = "-"

    if sample.nearest_ahead:

        ahead = (
            sample.nearest_ahead.driver_number
        )

        ahead_gap = (
            f"{sample.nearest_ahead.gap_progress:.6f}"
        )

    behind = "-"

    behind_gap = "-"

    if sample.nearest_behind:

        behind = (
            sample.nearest_behind.driver_number
        )

        behind_gap = (
            f"{sample.nearest_behind.gap_progress:.6f}"
        )

    print(

        f"{str(sample.session_time):<20}"

        f"{ahead:>8}"

        f"{ahead_gap:>14}"

        f"{behind:>10}"

        f"{behind_gap:>14}"

    )