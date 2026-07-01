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

from app.services.race_management.lap_traffic_analyzer import (
    LapTrafficAnalyzer,
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
# Analyze one lap
##############################################################

lap_samples = traffic_frame.samples_for_lap(
    LAP,
)

analysis = (
    LapTrafficAnalyzer()
    .analyze(
        lap_samples,
    )
)

##############################################################

print()

print("=" * 70)
print("LAP TRAFFIC ANALYSIS")
print("=" * 70)

print()

print("Driver :", DRIVER)
print("Lap    :", LAP)
print("Samples:", len(lap_samples))

print()

if analysis is None:

    print("No analysis available.")

else:

    print(
        "Nearest Ahead :",
        analysis.nearest_car_ahead,
    )

    print(
        "Gap Ahead     :",
        analysis.gap_ahead_progress,
    )

    print()

    print(
        "Nearest Behind:",
        analysis.nearest_car_behind,
    )

    print(
        "Gap Behind    :",
        analysis.gap_behind_progress,
    )

    print()

    print(
        "Dirty Air     :",
        analysis.in_dirty_air,
    )
    
    print(
        "Dirty Air %   :",
        f"{analysis.dirty_air_percentage:.1f}",
    )

    print(
        "Minimum Gap   :",
        f"{analysis.minimum_gap_ahead_progress:.6f}"
        if analysis.minimum_gap_ahead_progress is not None
        else "-",
    )
    
    print()

    print(
        "Representative Ahead:",
        analysis.nearest_car_ahead,
    )

    print(
        "Representative Behind:",
        analysis.nearest_car_behind,
    )

    print(
        "Traffic Score :",
        analysis.traffic_score,
    )

    print(
        "Representative:",
        analysis.representative,
    )