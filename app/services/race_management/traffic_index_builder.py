from app.services.race_management.telemetry_cursor import TelemetryCursor

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
        
        ##########################################################
        # One telemetry cursor per driver
        ##########################################################

        cursors = {}

        for other_driver, other_frame in collection.drivers.items():

            if other_driver == driver_number:
                continue

            cursors[other_driver] = TelemetryCursor(
                other_frame.samples
            )
            
        ##########################################################
        # Cache candidate drivers by lap
        ##########################################################

        candidate_cache = {}

        ##########################################################

        for sample in own_frame.samples:

            nearest_ahead = None
            nearest_behind = None

            smallest_positive = None
            smallest_negative = None

            ######################################################
            # Candidate drivers (cached per lap)
            ######################################################

            if sample.lap_number not in candidate_cache:

                candidate_cache[
                    sample.lap_number
                ] = self.candidate_service.get_candidates(

                    timeline,
                    driver_number,
                    sample.session_time,
                )

            candidates = candidate_cache[
                sample.lap_number
            ]

            ######################################################

            for other_driver in candidates:

                other_sample = cursors[
                    other_driver
                ].nearest(
                    sample.session_time
                )

                if other_sample is None:
                    continue

                ##################################################
                # Race gap
                ##################################################

                gap = self.gap_calculator.calculate_gap(

                    sample.lap_number,
                    sample.normalized_progress,

                    other_sample.lap_number,
                    other_sample.normalized_progress,
                )
                
                ##################################################
                # Convert lap progress into metres
                ##################################################

                gap_distance = abs(gap) * track_length

                ##################################################
                # Ahead
                ##################################################

                if gap > 0:

                    if (
                        smallest_positive is None
                        or gap < smallest_positive
                    ):

                        smallest_positive = gap

                        nearest_ahead = TrafficNeighbour(

                            driver_number=other_driver,

                            gap_progress=gap,

                            gap_distance=gap_distance,
                        )

                ##################################################
                # Behind
                ##################################################

                elif gap < 0:

                    absolute_gap = abs(gap)

                    if (
                        smallest_negative is None
                        or absolute_gap < smallest_negative
                    ):

                        smallest_negative = absolute_gap

                        nearest_behind = TrafficNeighbour(

                            driver_number=other_driver,

                            gap_progress=absolute_gap,

                            gap_distance=gap_distance,
                        )

            ######################################################

            traffic.samples.append(

                TrafficSample(

                    session_time=sample.session_time,

                    lap_number=sample.lap_number,

                    normalized_progress=(
                        sample.normalized_progress
                    ),

                    nearest_ahead=nearest_ahead,

                    nearest_behind=nearest_behind,
                )
            )

        ##########################################################

        return traffic

    ##############################################################
