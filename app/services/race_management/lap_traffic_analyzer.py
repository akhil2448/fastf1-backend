from .traffic_analyzer import TrafficAnalyzer
from .models import TrafficAnalysis
from .wake_model import WakeModel


class LapTrafficAnalyzer:
    """
    Analyzes traffic over an entire lap.

    Phase 2:

    Uses every telemetry sample in the lap to determine
    how representative the lap is.
    """

    REPRESENTATIVE_THRESHOLD = 85

    def __init__(
        self,
        traffic_analyzer: TrafficAnalyzer,
    ):
        self.traffic_analyzer = traffic_analyzer

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

        weighted_dirty_air_time = 0.0
        wake_sum = 0.0
        wake_samples = 0
        maximum_wake = 0.0
        dirty_air_time = 0.0
        minimum_gap_distance = None
        representative_follow_time = 0.0

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

                weight = self.traffic_analyzer.dirty_air_weight(
                    previous_analysis.gap_ahead_distance,
                    previous_sample.speed,
                    previous_sample.drs,
                )

                weighted_dirty_air_time += (
                    delta * weight
                )

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

                        "distance_sum": 0.0,
                    }

                if previous_sample is not None:

                    ahead_statistics[driver]["time"] += delta
                    
                    if analysis.gap_ahead_distance is not None:

                        ahead_statistics[driver]["distance_sum"] += (

                            analysis.gap_ahead_distance
                            * delta
                        )

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

                        "distance_sum": 0.0,
                    }

                if previous_sample is not None:

                    behind_statistics[driver]["time"] += delta
                    
                    if analysis.gap_behind_distance is not None:

                        behind_statistics[driver]["distance_sum"] += (

                            analysis.gap_behind_distance
                            * delta
                        )

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
        # Representative cars
        ##########################################################

        nearest_ahead = None
        nearest_behind = None

        minimum_gap = None
        gap_behind = None

        average_distance = None
        behind_average_distance = None

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
            
            time_following = (
                ahead_statistics[nearest_ahead]["time"]
            )

            if time_following > 0:

                average_distance = (

                    ahead_statistics[nearest_ahead]["distance_sum"]

                    / time_following

                )

            else:

                average_distance = None

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
            
            time_following = (
                behind_statistics[nearest_behind]["time"]
            )

            if time_following > 0:

                behind_average_distance = (

                    behind_statistics[nearest_behind]["distance_sum"]

                    / time_following

                )

            else:

                behind_average_distance = None
                
        representative_wake = None
        
        ##########################################################
        # Dirty air percentage
        # (Only while following the representative car)
        ##########################################################

        weighted_dirty_air_time = 0.0
        total_time = 0.0

        previous_sample = None
        previous_analysis = None

        for sample in traffic_samples:

            analysis = self.traffic_analyzer.analyze(sample)

            if previous_sample is not None:

                delta = (
                    sample.session_time
                    - previous_sample.session_time
                ).total_seconds()

                total_time += delta

                if (
                    previous_analysis.nearest_car_ahead
                    == nearest_ahead
                ):

                    representative_wake = previous_analysis.wake
                    
                    weight = representative_wake.final_weight

                    weighted_dirty_air_time += (
                        delta * weight
                    )
                    
                    ######################################################
                    # Wake statistics
                    ######################################################

                    wake_sum += weight

                    wake_samples += 1

                    maximum_wake = max(
                        maximum_wake,
                        weight,
                    )

                    representative_follow_time += delta

                    if weight > 0:

                        dirty_air_time += delta

                    ######################################################
                    # Minimum following distance
                    ######################################################

                    gap = previous_analysis.gap_ahead_distance

                    if gap is not None:

                        if (
                            minimum_gap_distance is None
                            or gap < minimum_gap_distance
                        ):

                            minimum_gap_distance = gap

            previous_sample = sample
            previous_analysis = analysis

        if total_time > 0:

            dirty_air_percentage = (
                weighted_dirty_air_time
                / total_time
            ) * 100

        else:

            dirty_air_percentage = 0.0
        
        
        ##########################################################
        # Summary statistics
        ##########################################################

        average_wake = (

            wake_sum / wake_samples

            if wake_samples

            else 0.0

        )

        time_in_dirty_air = (

            dirty_air_time

            / total_time

            * 100

            if total_time

            else 0.0

        )

        clean_air_percentage = (

            100 - time_in_dirty_air

        )

        following_time_percentage = (

            representative_follow_time

            / total_time

            * 100

            if total_time

            else 0.0

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
            
            gap_ahead_distance=average_distance,

            gap_behind_distance=behind_average_distance,

            in_dirty_air=(
                dirty_air_percentage > 0
            ),

            dirty_air_percentage=dirty_air_percentage,

            minimum_gap_ahead_progress=minimum_gap,

            traffic_score=score,

            clean_air_percentage=round(
                clean_air_percentage,
                1,
            ),

            time_in_dirty_air=round(
                time_in_dirty_air,
                1,
            ),

            average_wake_strength=round(
                average_wake,
                3,
            ),

            maximum_wake_strength=round(
                maximum_wake,
                3,
            ),

            average_gap_ahead_distance=(
                average_distance
            ),

            minimum_gap_ahead_distance=(
                minimum_gap_distance
            ),

            wake=representative_wake,

            representative=(
                score >= self.REPRESENTATIVE_THRESHOLD
            ),
        )

    ##############################################################
    
    # def _dirty_air_weight(
    #     self,
    #     gap_distance: float | None,
    # ) -> float:

    #     if gap_distance is None:
    #         return 0.0

    #     if gap_distance <= 40:
    #         return 1.00

    #     if gap_distance <= 80:
    #         return 0.80

    #     if gap_distance <= 120:
    #         return 0.50

    #     if gap_distance <= 180:
    #         return 0.20

    #     return 0.0
    
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