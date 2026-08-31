from __future__ import annotations

from time import perf_counter

from app.services.session_cache_service import (
    get_loaded_session,
)

from app.services.track_metrics_service import (
    build_track_metrics,
)

from app.services.telemetry_animation_service import (
    build_driver_telemetry_chunks,
)


YEAR = 2026
ROUND = 11
DRIVER = "ANT"


def main():

    print(
        f"Loading {YEAR} Round {ROUND}..."
    )

    session = get_loaded_session(
        YEAR,
        ROUND,
    )

    track_metrics = build_track_metrics(
        session
    )

    print(
        f"Building telemetry for {DRIVER}..."
    )

    start = perf_counter()

    result = build_driver_telemetry_chunks(
        session=session,
        driver_code=DRIVER,
        track_metrics=track_metrics,
    )

    total_time = (
        perf_counter() - start
    )

    print()
    print(
        "=" * 70
    )
    print(
        "CHUNK CONSTRUCTION BENCHMARK"
    )
    print(
        "=" * 70
    )

    print(
        "Driver:",
        DRIVER,
    )

    print(
        "Chunks:",
        len(result["chunks"]),
    )

    print(
        "Timing events:",
        len(result["timingEvents"]),
    )

    print(
        "Total driver generation:",
        f"{total_time:.6f}s",
    )

    print(
        "=" * 70
    )

    ##############################################################
    # Isolate final chunk construction using the same output
    ##############################################################

    # Extract the rows that would be used for final chunks by
    # reproducing the upstream pipeline from the already loaded
    # result is not possible because build_driver_telemetry_chunks()
    # returns only the final representation.
    #
    # Therefore this benchmark intentionally measures the complete
    # driver generation first. The stage-level timing already
    # isolates the chunk construction cost in production code.
    ##############################################################


if __name__ == "__main__":
    main()