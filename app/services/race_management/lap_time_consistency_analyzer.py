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
        stint_laps=None,
        window=None,
    ) -> LapTimeConsistency:

        ##########################################################
        # Collect neighbouring valid lap times
        ##########################################################

        if window is None:

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
        # Reasons
        ##########################################################

        reasons = []

        reasons.append(
            f"Median calculated from {len(window)} nearby laps"
        )

        if abs(delta) <= 0.10:

            reasons.append(
                f"Lap time within {abs(delta):.3f}s of expected pace"
            )

        elif abs(delta) <= 0.30:

            reasons.append(
                f"Lap time {abs(delta):.3f}s from expected pace"
            )

        elif delta < 0:

            reasons.append(
                f"Lap was {abs(delta):.3f}s quicker than expected"
            )

        else:

            reasons.append(
                f"Lap was {abs(delta):.3f}s slower than expected"
            )

        if score >= 95:

            reasons.append(
                "Excellent lap time consistency"
            )

        elif score >= 85:

            reasons.append(
                "Good lap time consistency"
            )

        elif score >= 70:

            reasons.append(
                "Moderate lap time consistency"
            )

        else:

            reasons.append(
                "Large deviation from expected lap time"
            )

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

            reasons=reasons,
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