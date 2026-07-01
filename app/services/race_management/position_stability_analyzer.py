from statistics import median

from .analysis_window_service import AnalysisWindowService
from .models import PositionStability


class PositionStabilityAnalyzer:

    REPRESENTATIVE_THRESHOLD = 85

    def __init__(self):

        self.window_service = AnalysisWindowService()

    ##############################################################

    def analyze(
        self,
        lap,
        stint_laps,
    ) -> PositionStability:

        ##########################################################
        # Neighbouring laps
        ##########################################################

        window = self.window_service.build_window(
            lap,
            stint_laps,
        )

        ##########################################################
        # Expected position
        ##########################################################

        positions = [
            candidate.position
            for candidate in window
        ]

        expected = median(positions)

        actual = lap.position

        delta = actual - expected

        ##########################################################

        score = self._calculate_score(delta)

        ##########################################################

        return PositionStability(

            expected_position=expected,

            actual_position=actual,

            delta_position=delta,

            score=score,

            representative=(
                score >= self.REPRESENTATIVE_THRESHOLD
            ),
        )

    ##############################################################

    def _calculate_score(
        self,
        delta_position: float,
    ) -> int:

        penalty = abs(delta_position) * 20

        score = round(100 - penalty)

        return max(
            0,
            min(
                100,
                score
            )
        )