from __future__ import annotations

from datetime import timedelta

import numpy as np

from .models import (
    TrafficFrame,
    TrafficSample,
    TrafficNeighbour,
)

from .traffic_candidate_service import (
    TrafficCandidateService,
)

from .race_gap_calculator import (
    RaceGapCalculator,
)


class TrafficIndexBuilder:
    """
    Builds traffic relationships for every telemetry sample.

    This builder does NOT determine dirty air or traffic score.

    It simply determines the nearest car ahead and behind.
    """

    def __init__(self):

        self.candidate_service = (
            TrafficCandidateService()
        )

        self.gap_calculator = (
            RaceGapCalculator()
        )

        #
        # Request-scoped numeric indexes.
        #
        # RaceManagementService uses the same builder instance
        # to process every driver for a race, so these arrays are
        # built once and reused across driver builds.
        #
        self._indexed_collection = None
        self._driver_indexes = {}

    ##############################################################
    # Numeric time conversion
    ##############################################################

    @staticmethod
    def _time_to_microseconds(
        value: timedelta,
    ) -> int:

        return (
            value.days * 86_400_000_000
            + value.seconds * 1_000_000
            + value.microseconds
        )

    ##############################################################
    # Build reusable numeric indexes
    ##############################################################

    def _ensure_driver_indexes(
        self,
        collection,
    ):

        #
        # Reuse the indexes when all driver builds belong to the
        # same RaceProgressCollection.
        #
        if (
            self._indexed_collection
            is collection
        ):
            return

        self._driver_indexes = {}

        for (
            other_driver,
            other_frame,
        ) in collection.drivers.items():

            samples = other_frame.samples

            times = np.asarray(
                [
                    self._time_to_microseconds(
                        sample.session_time
                    )
                    for sample in samples
                ],
                dtype=np.int64,
            )

            lap_numbers = np.asarray(
                [
                    sample.lap_number
                    for sample in samples
                ],
                dtype=np.int32,
            )

            progress = np.asarray(
                [
                    sample.normalized_progress
                    for sample in samples
                ],
                dtype=np.float64,
            )

            self._driver_indexes[
                other_driver
            ] = {
                "times": times,
                "lap_numbers": lap_numbers,
                "progress": progress,
            }

        self._indexed_collection = collection

    ##############################################################
    # Find nearest samples for MANY target times at once
    ##############################################################

    @classmethod
    def _nearest_indices(
        cls,
        sample_times: np.ndarray,
        target_times: np.ndarray,
    ) -> np.ndarray:

        if sample_times.size == 0:
            raise IndexError(
                "Cannot find nearest sample in an empty telemetry frame."
            )

        #
        # Match TelemetryCursor.nearest():
        #
        # current = last sample whose time <= target
        # next    = first sample whose time > target
        #
        # side="right" is important because it preserves the
        # existing behavior when duplicate timestamps exist.
        #
        right = np.searchsorted(
            sample_times,
            target_times,
            side="right",
        )

        current_index = np.maximum(
            right - 1,
            0,
        )

        next_index = np.minimum(
            right,
            sample_times.size - 1,
        )

        current_delta = np.abs(
            sample_times[current_index]
            - target_times
        )

        next_delta = np.abs(
            sample_times[next_index]
            - target_times
        )

        #
        # Match TelemetryCursor tie behavior:
        # current wins when the distances are equal.
        #
        return np.where(
            next_delta < current_delta,
            next_index,
            current_index,
        )

    ##############################################################
    # Build contiguous lap ranges
    ##############################################################

    @staticmethod
    def _build_lap_ranges(
        samples,
    ) -> list[tuple[int, int]]:

        if not samples:
            return []

        ranges = []

        start_index = 0
        current_lap = samples[0].lap_number

        for index in range(
            1,
            len(samples),
        ):

            if (
                samples[index].lap_number
                != current_lap
            ):

                ranges.append(
                    (
                        start_index,
                        index,
                    )
                )

                start_index = index
                current_lap = (
                    samples[index].lap_number
                )

        ranges.append(
            (
                start_index,
                len(samples),
            )
        )

        return ranges

    ##############################################################
    # Build traffic for one driver's complete frame
    ##############################################################

    def build(
        self,
        timeline,
        collection,
        track_length: float,
        driver_number: str,
    ) -> TrafficFrame:

        own_frame = collection.drivers[
            driver_number
        ]

        traffic = TrafficFrame(
            driver_number=driver_number,
        )

        if not own_frame.samples:
            return traffic

        #
        # Build/reuse numeric indexes for the entire race.
        #
        self._ensure_driver_indexes(
            collection
        )

        own_indexes = self._driver_indexes[
            driver_number
        ]

        own_samples = own_frame.samples

        #
        # Build traffic one lap at a time.
        #
        # This preserves the existing candidate cache behavior:
        # candidate drivers are determined once using the first
        # sample of a lap and reused for every sample in that lap.
        #
        lap_ranges = self._build_lap_ranges(
            own_samples
        )

        candidate_cache = {}

        for (
            start_index,
            end_index,
        ) in lap_ranges:

            lap_samples = own_samples[
                start_index:end_index
            ]

            lap_number = (
                lap_samples[0].lap_number
            )

            ######################################################
            # Candidate drivers
            ######################################################

            if lap_number not in candidate_cache:

                candidate_cache[
                    lap_number
                ] = (
                    self.candidate_service.get_candidates(
                        timeline,
                        driver_number,
                        lap_samples[0].session_time,
                    )
                )

            candidates = candidate_cache[
                lap_number
            ]

            ######################################################
            # No candidates
            ######################################################

            if not candidates:

                for sample in lap_samples:

                    traffic.samples.append(
                        TrafficSample(
                            session_time=sample.session_time,
                            lap_number=sample.lap_number,
                            normalized_progress=(
                                sample.normalized_progress
                            ),
                            speed=sample.speed,
                            drs=sample.drs,
                            nearest_ahead=None,
                            nearest_behind=None,
                        )
                    )

                continue

            ######################################################
            # Own sample arrays
            ######################################################

            target_times = np.asarray(
                [
                    self._time_to_microseconds(
                        sample.session_time
                    )
                    for sample in lap_samples
                ],
                dtype=np.int64,
            )

            own_laps = np.asarray(
                [
                    sample.lap_number
                    for sample in lap_samples
                ],
                dtype=np.int32,
            )

            own_progress = np.asarray(
                [
                    sample.normalized_progress
                    for sample in lap_samples
                ],
                dtype=np.float64,
            )

            sample_count = len(
                lap_samples
            )

            candidate_count = len(
                candidates
            )

            ######################################################
            # Gap matrix
            #
            # rows    = own telemetry samples
            # columns = candidate drivers
            #
            # This replaces millions of Python-level nearest()
            # and gap calculations with a small number of
            # vectorized operations.
            ######################################################

            gaps = np.empty(
                (
                    sample_count,
                    candidate_count,
                ),
                dtype=np.float64,
            )

            candidate_sample_indexes = []

            for candidate_index, other_driver in enumerate(
                candidates
            ):

                other_indexes = (
                    self._driver_indexes[
                        other_driver
                    ]
                )

                nearest_indexes = (
                    self._nearest_indices(
                        other_indexes["times"],
                        target_times,
                    )
                )

                candidate_sample_indexes.append(
                    nearest_indexes
                )

                other_laps = (
                    other_indexes[
                        "lap_numbers"
                    ][nearest_indexes]
                )

                other_progress = (
                    other_indexes[
                        "progress"
                    ][nearest_indexes]
                )

                #
                # This is mathematically identical to:
                #
                # RaceGapCalculator.calculate_gap(...)
                #
                # We use it only to determine the winner.
                # The final selected gap is recalculated through
                # RaceGapCalculator below.
                #
                gaps[
                    :,
                    candidate_index,
                ] = (
                    other_laps
                    - own_laps
                    + (
                        other_progress
                        - own_progress
                    )
                )

            ######################################################
            # Nearest car ahead
            ######################################################

            positive_gaps = np.where(
                gaps > 0,
                gaps,
                np.inf,
            )

            ahead_candidate_indexes = (
                np.argmin(
                    positive_gaps,
                    axis=1,
                )
            )

            ahead_values = (
                positive_gaps[
                    np.arange(
                        sample_count
                    ),
                    ahead_candidate_indexes,
                ]
            )

            ######################################################
            # Nearest car behind
            ######################################################

            negative_gaps = np.where(
                gaps < 0,
                -gaps,
                np.inf,
            )

            behind_candidate_indexes = (
                np.argmin(
                    negative_gaps,
                    axis=1,
                )
            )

            behind_values = (
                negative_gaps[
                    np.arange(
                        sample_count
                    ),
                    behind_candidate_indexes,
                ]
            )

            ######################################################
            # Create final TrafficSample objects
            ######################################################

            for sample_index, sample in enumerate(
                lap_samples
            ):

                nearest_ahead = None
                nearest_behind = None

                ##################################################
                # Ahead
                ##################################################

                if np.isfinite(
                    ahead_values[sample_index]
                ):

                    candidate_index = int(
                        ahead_candidate_indexes[
                            sample_index
                        ]
                    )

                    other_driver = candidates[
                        candidate_index
                    ]

                    other_sample_index = int(
                        candidate_sample_indexes[
                            candidate_index
                        ][sample_index]
                    )

                    other_sample = (
                        collection
                        .drivers[
                            other_driver
                        ]
                        .samples[
                            other_sample_index
                        ]
                    )

                    #
                    # Recalculate using the existing calculator
                    # to preserve the exact Python calculation
                    # used by the old implementation.
                    #
                    gap = (
                        self.gap_calculator.calculate_gap(
                            sample.lap_number,
                            sample.normalized_progress,
                            other_sample.lap_number,
                            other_sample.normalized_progress,
                        )
                    )

                    if gap > 0:

                        gap_distance = (
                            abs(gap)
                            * track_length
                        )

                        nearest_ahead = (
                            TrafficNeighbour(
                                driver_number=other_driver,
                                gap_progress=gap,
                                gap_distance=gap_distance,
                            )
                        )

                ##################################################
                # Behind
                ##################################################

                if np.isfinite(
                    behind_values[sample_index]
                ):

                    candidate_index = int(
                        behind_candidate_indexes[
                            sample_index
                        ]
                    )

                    other_driver = candidates[
                        candidate_index
                    ]

                    other_sample_index = int(
                        candidate_sample_indexes[
                            candidate_index
                        ][sample_index]
                    )

                    other_sample = (
                        collection
                        .drivers[
                            other_driver
                        ]
                        .samples[
                            other_sample_index
                        ]
                    )

                    #
                    # Preserve the exact existing gap
                    # calculation.
                    #
                    gap = (
                        self.gap_calculator.calculate_gap(
                            sample.lap_number,
                            sample.normalized_progress,
                            other_sample.lap_number,
                            other_sample.normalized_progress,
                        )
                    )

                    if gap < 0:

                        absolute_gap = abs(
                            gap
                        )

                        gap_distance = (
                            absolute_gap
                            * track_length
                        )

                        nearest_behind = (
                            TrafficNeighbour(
                                driver_number=other_driver,
                                gap_progress=absolute_gap,
                                gap_distance=gap_distance,
                            )
                        )

                traffic.samples.append(
                    TrafficSample(
                        session_time=sample.session_time,
                        lap_number=sample.lap_number,
                        normalized_progress=(
                            sample.normalized_progress
                        ),
                        speed=sample.speed,
                        drs=sample.drs,
                        nearest_ahead=nearest_ahead,
                        nearest_behind=nearest_behind,
                    )
                )

        return traffic