from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.services.session_cache_service import (
    get_loaded_session,
)

from app.services.telemetry_animation_chunk_writer import (
    generate_race_telemetry,
)

from app.services.telemetry_animation_service import (
    build_driver_telemetry_chunks,
)

from app.dev_tools.telemetry_animation_service_legacy import (
    build_driver_telemetry_chunks as legacy_build_driver_telemetry_chunks,
)


YEAR = 2026
ROUND = 11

BASELINE_FILE = Path(
    "performance_baselines/telemetry_animation/"
    f"baseline_{YEAR}_{ROUND}.json"
)


def hash_json(payload) -> str:
    """
    Produce the same canonical JSON representation used
    for the baseline file and return its SHA-256 hash.
    """

    encoded = json.dumps(
        payload,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()

def canonicalize(payload):
    """
    Convert the payload through JSON so that Python and
    JSON representations use identical key/value types.
    """

    return json.loads(
        json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
    )

def compare_values(
    legacy,
    optimized,
    path="root",
):
    """
    Recursively compare two telemetry structures.

    Raises AssertionError at the first exact mismatch.
    """

    if type(legacy) is not type(optimized):

        raise AssertionError(
            f"Type mismatch at {path}: "
            f"{type(legacy).__name__} != "
            f"{type(optimized).__name__}"
        )

    if isinstance(legacy, dict):

        if legacy.keys() != optimized.keys():

            raise AssertionError(
                f"Key mismatch at {path}\n"
                f"Legacy keys: {legacy.keys()}\n"
                f"Optimized keys: {optimized.keys()}"
            )

        for key in legacy:

            compare_values(
                legacy[key],
                optimized[key],
                f"{path}[{key!r}]",
            )

        return

    if isinstance(legacy, list):

        if len(legacy) != len(optimized):

            raise AssertionError(
                f"Length mismatch at {path}: "
                f"{len(legacy)} != {len(optimized)}"
            )

        for index, (
            legacy_value,
            optimized_value,
        ) in enumerate(
            zip(
                legacy,
                optimized,
            )
        ):

            compare_values(
                legacy_value,
                optimized_value,
                f"{path}[{index}]",
            )

        return

    if legacy != optimized:

        raise AssertionError(
            f"Value mismatch at {path}\n"
            f"Legacy:    {legacy!r}\n"
            f"Optimized: {optimized!r}"
        )


def main():

    print(
        f"Loading {YEAR} Round {ROUND}..."
    )

    session = get_loaded_session(
        YEAR,
        ROUND,
    )

    ##############################################################
    # Track metrics
    ##############################################################

    from app.services.track_metrics_service import (
        build_track_metrics,
    )

    track_metrics = build_track_metrics(
        session
    )

    ##############################################################
    # Compare every driver
    ##############################################################

    drivers = sorted(
        session.laps["Driver"]
        .dropna()
        .unique()
    )

    drivers_tested = 0
    total_chunks = 0
    total_events = 0

    print()
    print("=" * 70)
    print("TELEMETRY ANIMATION VALIDATION")
    print("=" * 70)

    for driver in drivers:

        print()
        print(
            f"Testing driver: {driver}"
        )

        ##########################################################
        # Legacy
        ##########################################################

        print(
            "Building legacy telemetry..."
        )

        legacy_result = (
            legacy_build_driver_telemetry_chunks(
                session=session,
                driver_code=driver,
                track_metrics=track_metrics,
            )
        )

        ##########################################################
        # Optimized
        ##########################################################

        print(
            "Building optimized telemetry..."
        )

        optimized_result = (
            build_driver_telemetry_chunks(
                session=session,
                driver_code=driver,
                track_metrics=track_metrics,
            )
        )

        ##########################################################
        # Compare
        ##########################################################

        compare_values(
            legacy_result,
            optimized_result,
            path=f"driver[{driver!r}]",
        )

        print(
            f"PASS {driver}: "
            f"{len(optimized_result['chunks'])} chunks, "
            f"{len(optimized_result['timingEvents'])} events"
        )

        drivers_tested += 1
        total_chunks += len(
            optimized_result["chunks"]
        )
        total_events += len(
            optimized_result["timingEvents"]
        )

    ##############################################################
    # Compare complete race generation
    ##############################################################

    print()
    print(
        "Building complete legacy race telemetry..."
    )

    legacy_all_chunks = {}

    legacy_timing_events = []

    for driver in drivers:

        driver_result = (
            legacy_build_driver_telemetry_chunks(
                session=session,
                driver_code=driver,
                track_metrics=track_metrics,
            )
        )

        legacy_timing_events.extend(
            driver_result["timingEvents"]
        )

        for second, snapshot in (
            driver_result["chunks"].items()
        ):

            legacy_all_chunks.setdefault(
                second,
                [],
            ).append(snapshot)

    legacy_timing_events.sort(
        key=lambda event: event["raceTime"]
    )

    legacy_frames = {}

    for second in sorted(
        legacy_all_chunks.keys()
    ):

        cars = legacy_all_chunks[second]

        if not cars:
            continue

        legacy_frames[int(second)] = {
            "raceTime": int(second),
            "cars": sorted(
                cars,
                key=lambda car: car["driver"],
            ),
        }

    legacy_complete = {
        "frames": legacy_frames,
        "timingEvents": legacy_timing_events,
    }

    print(
        "Building complete optimized race telemetry..."
    )

    optimized_complete = (
        generate_race_telemetry(
            session
        )
    )

    compare_values(
        legacy_complete,
        optimized_complete,
        path="race",
    )

    ##############################################################
    # Compare against frozen baseline
    ##############################################################

    if not BASELINE_FILE.exists():

        raise AssertionError(
            f"Baseline file not found: {BASELINE_FILE}"
        )

    with BASELINE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        baseline = json.load(file)

    compare_values(
        canonicalize(baseline),
        canonicalize(optimized_complete),
        path="baseline",
    )

    baseline_hash = hash_json(
        canonicalize(baseline)
    )

    optimized_hash = hash_json(
        canonicalize(optimized_complete)
    )

    print()
    print("=" * 70)
    print("TELEMETRY ANIMATION VALIDATION PASSED")
    print("=" * 70)

    print(
        "Drivers tested:",
        drivers_tested,
    )

    print(
        "Total chunks checked:",
        total_chunks,
    )

    print(
        "Total timing events checked:",
        total_events,
    )

    print(
        "Baseline SHA-256:",
        baseline_hash,
    )

    print(
        "Optimized SHA-256:",
        optimized_hash,
    )

    if baseline_hash != optimized_hash:

        raise AssertionError(
            "Baseline and optimized JSON hashes differ."
        )

    print(
        "Baseline JSON: IDENTICAL"
    )


if __name__ == "__main__":
    main()