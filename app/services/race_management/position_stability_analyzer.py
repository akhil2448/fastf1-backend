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
        stint_laps=None,
        window=None,
    ) -> PositionStability:

        ##########################################################
        # Neighbouring laps
        ##########################################################

        if window is None:

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
        # Reasons
        ##########################################################

        reasons = []

        reasons.append(
            f"Expected running position P{round(expected)}"
        )

        ##########################################################
        # Position delta
        ##########################################################

        if delta == 0:

            reasons.append(
                f"Maintained position P{actual}"
            )

        elif abs(delta) <= 1:

            reasons.append(
                f"Running close to expected position (P{actual})"
            )

        elif delta < 0:

            reasons.append(
                f"Gained {abs(int(delta))} position(s)"
            )

        else:

            reasons.append(
                f"Lost {int(delta)} position(s)"
            )

        ##########################################################
        # Overall
        ##########################################################

        if score >= 95:

            reasons.append(
                "Excellent position stability"
            )

        elif score >= 85:

            reasons.append(
                "Stable race position"
            )

        elif score >= 70:

            reasons.append(
                "Minor position changes"
            )

        else:

            reasons.append(
                "Large position changes during stint"
            )

        ##########################################################

        return PositionStability(

            expected_position=expected,

            actual_position=actual,

            delta_position=delta,

            score=score,

            representative=(
                score >= self.REPRESENTATIVE_THRESHOLD
            ),
            reasons=reasons,
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