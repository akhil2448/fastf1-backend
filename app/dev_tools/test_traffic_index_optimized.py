from __future__ import annotations

from app.services.session_cache_service import get_loaded_session

from app.services.race_management.race_progress_collection_service import (
    RaceProgressCollectionService,
)
from app.services.race_management.race_progress_service import (
    RaceProgressService,
)
from app.services.race_management.race_timeline_service import (
    RaceTimelineService,
)
from app.services.race_management.track_length_service import (
    TrackLengthService,
)
from app.services.race_management.traffic_candidate_service import (
    TrafficCandidateService,
)
from app.services.race_management.race_gap_calculator import (
    RaceGapCalculator,
)
from app.services.race_management.telemetry_cursor import (
    TelemetryCursor,
)
from app.services.race_management.traffic_index_builder import (
    TrafficIndexBuilder,
)

from app.dev_tools.telemetry_service_legacy import (
    TelemetryService as LegacyTelemetryService,
)

from app.services.race_management.telemetry_service import (
    TelemetryService,
)


YEAR = 2026
ROUND = 2


class LegacyTrafficIndexBuilder:

    def __init__(self):

        self.candidate_service = (
            TrafficCandidateService()
        )

        self.gap_calculator = (
            RaceGapCalculator()
        )

    def build(
        self,
        timeline,
        collection,
        track_length: float,
        driver_number: str,
    ):

        own_frame = collection.drivers[
            driver_number
        ]

        cursors = {}

        for (
            other_driver,
            other_frame,
        ) in collection.drivers.items():

            if other_driver == driver_number:
                continue

            cursors[other_driver] = (
                TelemetryCursor(
                    other_frame.samples
                )
            )

        candidate_cache = {}

        traffic_samples = []

        for sample in own_frame.samples:

            nearest_ahead = None
            nearest_behind = None

            smallest_positive = None
            smallest_negative = None

            if sample.lap_number not in candidate_cache:

                candidate_cache[
                    sample.lap_number
                ] = (
                    self.candidate_service.get_candidates(
                        timeline,
                        driver_number,
                        sample.session_time,
                    )
                )

            candidates = candidate_cache[
                sample.lap_number
            ]

            for other_driver in candidates:

                other_sample = cursors[
                    other_driver
                ].nearest(
                    sample.session_time
                )

                if other_sample is None:
                    continue

                gap = (
                    self.gap_calculator.calculate_gap(
                        sample.lap_number,
                        sample.normalized_progress,
                        other_sample.lap_number,
                        other_sample.normalized_progress,
                    )
                )

                gap_distance = (
                    abs(gap)
                    * track_length
                )

                if gap > 0:

                    if (
                        smallest_positive is None
                        or gap < smallest_positive
                    ):

                        smallest_positive = gap

                        nearest_ahead = (
                            (
                                other_driver,
                                gap,
                                gap_distance,
                            )
                        )

                elif gap < 0:

                    absolute_gap = abs(gap)

                    if (
                        smallest_negative is None
                        or absolute_gap
                        < smallest_negative
                    ):

                        smallest_negative = (
                            absolute_gap
                        )

                        nearest_behind = (
                            (
                                other_driver,
                                absolute_gap,
                                gap_distance,
                            )
                        )

            traffic_samples.append(
                (
                    sample,
                    nearest_ahead,
                    nearest_behind,
                )
            )

        return traffic_samples


def build_progress_collection(
    session,
    telemetry_service,
):
    """
    Build a RaceProgressCollection using the supplied
    TelemetryService implementation.
    """

    progress_service = (
        RaceProgressService()
    )

    collection = (
        RaceProgressCollectionService()
    )

    collection.drivers = {}

    for driver_number in session.drivers:

        telemetry = (
            telemetry_service.build(
                session,
                driver_number,
            )
        )

        progress = (
            progress_service.build(
                telemetry
            )
        )

        collection.drivers[
            driver_number
        ] = progress

    return collection


def normalize_traffic_frame(
    traffic_frame,
):
    """
    Convert TrafficFrame into simple tuples so the
    comparison focuses on the actual traffic decisions.
    """

    result = []

    for sample in traffic_frame.samples:

        ahead = None

        if sample.nearest_ahead is not None:

            ahead = (
                sample.nearest_ahead.driver_number,
                sample.nearest_ahead.gap_progress,
                sample.nearest_ahead.gap_distance,
            )

        behind = None

        if sample.nearest_behind is not None:

            behind = (
                sample.nearest_behind.driver_number,
                sample.nearest_behind.gap_progress,
                sample.nearest_behind.gap_distance,
            )

        result.append(
            (
                sample.session_time,
                sample.lap_number,
                sample.normalized_progress,
                sample.speed,
                sample.drs,
                ahead,
                behind,
            )
        )

    return result


def normalize_legacy_samples(
    traffic_samples,
):
    """
    Convert the legacy result into the same comparison format.
    """

    result = []

    for (
        sample,
        ahead,
        behind,
    ) in traffic_samples:

        result.append(
            (
                sample.session_time,
                sample.lap_number,
                sample.normalized_progress,
                sample.speed,
                sample.drs,
                ahead,
                behind,
            )
        )

    return result


def main():

    print(
        f"Loading {YEAR} Round {ROUND}..."
    )

    session = get_loaded_session(
        YEAR,
        ROUND,
    )

    timeline = (
        RaceTimelineService().build(
            session
        )
    )

    track_length = (
        TrackLengthService().get_track_length(
            session
        )
    )

    ##############################################################
    # Build LEGACY collection
    ##############################################################

    print()
    print(
        "Building legacy RaceProgressCollection..."
    )

    legacy_telemetry_service = (
        LegacyTelemetryService()
    )

    legacy_collection = (
        build_progress_collection(
            session,
            legacy_telemetry_service,
        )
    )

    ##############################################################
    # Build OPTIMIZED collection
    ##############################################################

    print()
    print(
        "Building optimized RaceProgressCollection..."
    )

    optimized_telemetry_service = (
        TelemetryService()
    )

    optimized_collection = (
        build_progress_collection(
            session,
            optimized_telemetry_service,
        )
    )

    ##############################################################
    # Builders
    ##############################################################

    legacy_builder = (
        LegacyTrafficIndexBuilder()
    )

    optimized_builder = (
        TrafficIndexBuilder()
    )

    ##############################################################
    # Compare every driver
    ##############################################################

    drivers_tested = 0
    total_samples_checked = 0

    print()
    print("=" * 70)
    print("TRAFFIC INDEX VALIDATION")
    print("=" * 70)

    for driver_number, legacy_frame in (
        legacy_collection.drivers.items()
    ):

        optimized_frame = (
            optimized_collection.drivers.get(
                driver_number
            )
        )

        if (
            optimized_frame is None
            or not legacy_frame.samples
        ):

            print(
                f"SKIP {driver_number}: "
                "no telemetry samples"
            )

            continue

        print()
        print(
            f"Testing driver: {driver_number}"
        )

        print(
            "Building legacy traffic..."
        )

        legacy_result = (
            legacy_builder.build(
                timeline,
                legacy_collection,
                track_length,
                driver_number,
            )
        )

        print(
            "Building optimized traffic..."
        )

        optimized_result = (
            optimized_builder.build(
                timeline,
                optimized_collection,
                track_length,
                driver_number,
            )
        )

        legacy_normalized = (
            normalize_legacy_samples(
                legacy_result
            )
        )

        optimized_normalized = (
            normalize_traffic_frame(
                optimized_result
            )
        )

        print(
            "Legacy samples    :",
            len(legacy_normalized),
        )

        print(
            "Optimized samples :",
            len(optimized_normalized),
        )

        if len(legacy_normalized) != len(
            optimized_normalized
        ):

            raise AssertionError(
                f"Traffic sample count mismatch "
                f"for driver {driver_number}"
            )

        for index, (
            legacy,
            optimized,
        ) in enumerate(
            zip(
                legacy_normalized,
                optimized_normalized,
            )
        ):

            if legacy != optimized:

                print()
                print(
                    "MISMATCH FOUND"
                )

                print(
                    "Driver:",
                    driver_number,
                )

                print(
                    "Sample index:",
                    index,
                )

                print(
                    "Legacy:",
                    legacy,
                )

                print(
                    "Optimized:",
                    optimized,
                )

                raise AssertionError(
                    "Optimized TrafficIndexBuilder "
                    f"does not match legacy output "
                    f"for driver {driver_number}."
                )

        print(
            f"PASS {driver_number}: "
            "traffic output matches legacy."
        )

        drivers_tested += 1

        total_samples_checked += len(
            optimized_normalized
        )

    print()
    print("=" * 70)
    print("TRAFFIC INDEX VALIDATION PASSED")
    print("=" * 70)

    print(
        "Drivers tested:",
        drivers_tested,
    )

    print(
        "Total samples checked:",
        total_samples_checked,
    )


if __name__ == "__main__":
    main()