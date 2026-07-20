from app.services.session_cache_service import get_loaded_session

from app.services.race_management.race_timeline_service import (
    RaceTimelineService,
)

from app.services.race_management.race_progress_collection_service import (
    RaceProgressCollectionService,
)

from app.services.race_management.track_length_service import (
    TrackLengthService,
)

from app.services.race_management.traffic_index_builder import (
    TrafficIndexBuilder,
)

from app.services.race_management.traffic_analyzer import (
    TrafficAnalyzer,
)

YEAR = 2024
ROUND = 11

DRIVER = "44"
LAP = 7


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

track_length = (
    TrackLengthService()
    .get_track_length(session)
)

traffic_frame = (
    TrafficIndexBuilder()
    .build(
        timeline,
        collection,
        track_length,
        DRIVER,
    )
)

samples = traffic_frame.samples_for_lap(
    LAP,
)

analyzer = TrafficAnalyzer()

print()
print("=" * 120)
print(f"DIRTY AIR TRACE - Driver {DRIVER} Lap {LAP}")
print("=" * 120)
print()

print(
    f"{'Time':<18}"
    f"{'Ahead':>8}"
    f"{'Dist(m)':>12}"
    f"{'Gap':>10}"
    f"{'Dirty':>10}"
)

print("-" * 120)

for sample in samples:

    analysis = analyzer.analyze(sample)

    print(

        f"{str(sample.session_time):<18}"

        f"{str(analysis.nearest_car_ahead):>8}"

        f"{analysis.gap_ahead_distance if analysis.gap_ahead_distance is not None else '-':>12}"

        f"{analysis.gap_ahead_progress if analysis.gap_ahead_progress is not None else '-':>10}"

        f"{str(analysis.in_dirty_air):>10}"

    )