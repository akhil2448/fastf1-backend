from .models import TrafficAnalysis
from .wake_model import WakeModel


class TrafficAnalyzer:

    """
    Converts a TrafficSample into a TrafficAnalysis.

    Phase 1:

    • nearest cars
    • simple dirty-air detection
    • traffic score
    """
    
    REPRESENTATIVE_THRESHOLD = 85
    
    def __init__(self):
        self.wake_model = WakeModel()


    ##############################################################

    # DIRTY_AIR_THRESHOLD = 0.030
    # DIRTY_AIR_DISTANCE = 80.0

    ##############################################################

    def analyze(
        self,
        traffic_sample,
    ) -> TrafficAnalysis:

        ##########################################################
        # Ahead
        ##########################################################

        ahead_driver = None
        ahead_gap = None
        ahead_distance = None

        if traffic_sample.nearest_ahead:

            ahead_driver = (
                traffic_sample
                .nearest_ahead
                .driver_number
            )

            ahead_gap = (
                traffic_sample
                .nearest_ahead
                .gap_progress
            )

            ahead_distance = (
                traffic_sample
                .nearest_ahead
                .gap_distance
            )

        ##########################################################
        # Behind
        ##########################################################

        behind_driver = None
        behind_gap = None
        behind_distance = None
        
        if traffic_sample.nearest_behind:

            behind_driver = (
                traffic_sample
                .nearest_behind
                .driver_number
            )

            behind_gap = (
                traffic_sample
                .nearest_behind
                .gap_progress
            )
            
            behind_distance = (
                traffic_sample
                .nearest_behind
                .gap_distance
            )

        ##########################################################
        # Dirty air
        ##########################################################

        in_dirty_air = self.wake_model.is_dirty_air(
            ahead_distance,
        )

        ##########################################################
        # Score
        ##########################################################

        score = self._calculate_score(
            ahead_gap,
            in_dirty_air,
        )

        ##########################################################

        return TrafficAnalysis(

            nearest_car_ahead=ahead_driver,

            gap_ahead_progress=ahead_gap,

            nearest_car_behind=behind_driver,

            gap_behind_progress=behind_gap,
            
            gap_ahead_distance=ahead_distance,

            gap_behind_distance=behind_distance,

            in_dirty_air=in_dirty_air,

            dirty_air_percentage=(
                100.0 if in_dirty_air else 0.0
            ),

            minimum_gap_ahead_progress=ahead_gap,

            traffic_score=score,

            representative=(
                score >= self.REPRESENTATIVE_THRESHOLD
            ),
        )
        

        ##############################################################

    def _calculate_score(
        self,
        ahead_gap: float | None,
        in_dirty_air: bool,
    ) -> int:

        ##########################################################
        # No car ahead
        ##########################################################

        if ahead_gap is None:
            return 100

        ##########################################################
        # Dirty air
        ##########################################################

        if in_dirty_air:
            return 60

        ##########################################################
        # Traffic ahead but not close enough
        ##########################################################

        return 90
    
    ##############################################################

    # def _is_dirty_air(
    #     self,
    #     ahead_distance: float | None,
    # ) -> bool:

    #     if ahead_distance is None:
    #         return False

    #     return (
    #         ahead_distance
    #         <= self.DIRTY_AIR_DISTANCE
    #     )