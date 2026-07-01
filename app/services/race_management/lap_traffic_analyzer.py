from .traffic_analyzer import TrafficAnalyzer
from .models import TrafficAnalysis


class LapTrafficAnalyzer:
    """
    Analyzes traffic over an entire lap.

    Phase 2:

    Uses every telemetry sample in the lap to determine
    how representative the lap is.
    """

    REPRESENTATIVE_THRESHOLD = 85

    def __init__(self):

        self.traffic_analyzer = (
            TrafficAnalyzer()
        )

    ##############################################################

    def analyze(
        self,
        traffic_samples,
    ) -> TrafficAnalysis | None:

        if not traffic_samples:
            return None

        ##########################################################
        # Statistics
        ##########################################################

        dirty_air_time = 0.0

        total_time = 0.0

        ahead_statistics = {}

        behind_statistics = {}

        ##########################################################

        ##########################################################
        # Analyze consecutive telemetry samples
        ##########################################################

        previous_sample = None

        previous_analysis = None

        for sample in traffic_samples:

            analysis = self.traffic_analyzer.analyze(
                sample
            )

            ######################################################
            # Accumulate elapsed time
            ######################################################

            if previous_sample is not None:

                delta = (

                    sample.session_time

                    - previous_sample.session_time

                ).total_seconds()

                total_time += delta

                if previous_analysis.in_dirty_air:

                    dirty_air_time += delta

            ######################################################
            # Track car ahead
            ######################################################

            if analysis.nearest_car_ahead is not None:

                driver = analysis.nearest_car_ahead

                if driver not in ahead_statistics:

                    ahead_statistics[driver] = {

                        "time": 0.0,

                        "minimum_gap": (
                            analysis.gap_ahead_progress
                        ),
                    }

                if previous_sample is not None:

                    ahead_statistics[driver]["time"] += delta

                gap = analysis.gap_ahead_progress

                current_minimum = (
                    ahead_statistics[driver]["minimum_gap"]
                )

                if (
                    gap is not None
                    and
                    (
                        current_minimum is None
                        or gap < current_minimum
                    )
                ):

                    ahead_statistics[driver]["minimum_gap"] = gap

            ######################################################
            # Track car behind
            ######################################################

            if analysis.nearest_car_behind is not None:

                driver = analysis.nearest_car_behind

                if driver not in behind_statistics:

                    behind_statistics[driver] = {

                        "time": 0.0,

                        "minimum_gap": (
                            analysis.gap_behind_progress
                        ),
                    }

                if previous_sample is not None:

                    behind_statistics[driver]["time"] += delta

                gap = analysis.gap_behind_progress

                current_minimum = (
                    behind_statistics[driver]["minimum_gap"]
                )

                if (
                    gap is not None
                    and
                    (
                        current_minimum is None
                        or gap < current_minimum
                    )
                ):

                    behind_statistics[driver]["minimum_gap"] = gap

            previous_sample = sample

            previous_analysis = analysis

        ##########################################################
        # Dirty air percentage
        ##########################################################

        if total_time > 0:

            dirty_air_percentage = (

                dirty_air_time
                / total_time

            ) * 100

        else:

            dirty_air_percentage = 0.0
            
        ##########################################################
        # Representative cars
        ##########################################################

        nearest_ahead = None

        nearest_behind = None

        minimum_gap = None

        gap_behind = None

        if ahead_statistics:

            nearest_ahead = max(

                ahead_statistics,

                key=lambda driver:
                ahead_statistics[driver]["time"],
            )

            minimum_gap = (
                ahead_statistics[nearest_ahead][
                    "minimum_gap"
                ]
            )

        if behind_statistics:

            nearest_behind = max(

                behind_statistics,

                key=lambda driver:
                behind_statistics[driver]["time"],
            )

            gap_behind = (
                behind_statistics[nearest_behind][
                    "minimum_gap"
                ]
            )

        ##########################################################
        # Score
        ##########################################################

        score = self._calculate_score(
            dirty_air_percentage
        )

        ##########################################################

        return TrafficAnalysis(

            nearest_car_ahead=nearest_ahead,

            gap_ahead_progress=minimum_gap,

            nearest_car_behind=nearest_behind,

            gap_behind_progress=gap_behind,

            in_dirty_air=(
                dirty_air_percentage > 0
            ),

            dirty_air_percentage=dirty_air_percentage,

            minimum_gap_ahead_progress=minimum_gap,

            traffic_score=score,

            representative=(
                score >= self.REPRESENTATIVE_THRESHOLD
            ),
        )

    ##############################################################

    def _calculate_score(
        self,
        dirty_air_percentage: float,
    ) -> int:

        if dirty_air_percentage >= 60:
            return 40

        if dirty_air_percentage >= 40:
            return 60

        if dirty_air_percentage >= 20:
            return 75

        if dirty_air_percentage >= 5:
            return 90

        return 100