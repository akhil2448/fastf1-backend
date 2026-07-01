from statistics import median

from .models import LapTimeConsistency
from .analysis_window_service import AnalysisWindowService


class LapTimeConsistencyAnalyzer:
    
    def __init__(self):

        self.window_service = AnalysisWindowService()

    """
    Evaluates how representative a lap time is compared to
    neighbouring laps within the same stint.
    """

    REPRESENTATIVE_THRESHOLD = 85

    def analyze(
        self,
        lap,
        stint_laps,
    ) -> LapTimeConsistency:

        ##########################################################
        # Collect neighbouring valid lap times
        ##########################################################

        window = self.window_service.build_window(
            lap,
            stint_laps,
        )

        ##########################################################
        # Convert lap times to seconds
        ##########################################################

        lap_times = [
            candidate.lap_time.total_seconds()
            for candidate in window
        ]

        expected = median(lap_times)

        actual = lap.lap_time.total_seconds()

        delta = actual - expected

        ##########################################################
        # Score
        ##########################################################

        score = self._calculate_score(delta)

        ##########################################################

        return LapTimeConsistency(

            expected_lap_time=expected,

            actual_lap_time=actual,

            delta_seconds=delta,

            median_window_size=len(window),

            score=score,

            representative=(
                score >= self.REPRESENTATIVE_THRESHOLD
            ),
        )

    ##############################################################

    def _calculate_score(
        self,
        delta_seconds: float,
    ) -> int:

        penalty = abs(delta_seconds) * 25

        score = round(100 - penalty)

        return max(
            0,
            min(
                100,
                score
            )
        )