from statistics import median

from .models import SectorConsistency
from .analysis_window_service import AnalysisWindowService


class SectorConsistencyAnalyzer:
    
    def __init__(self):

        self.window_service = AnalysisWindowService()
    
    """
    Evaluates how representative each sector is compared to the
    neighbouring valid laps within the same stint.
    """

    REPRESENTATIVE_THRESHOLD = 85

    def analyze(
        self,
        lap,
        stint_laps,
    ) -> SectorConsistency:

        ##########################################################
        # Build analysis window
        ##########################################################

        window = self.window_service.build_window(
            lap,
            stint_laps,
        )

        ##########################################################
        # Sector arrays
        ##########################################################

        sector1 = [
            candidate.sector1_time.total_seconds()
            for candidate in window
        ]

        sector2 = [
            candidate.sector2_time.total_seconds()
            for candidate in window
        ]

        sector3 = [
            candidate.sector3_time.total_seconds()
            for candidate in window
        ]

        ##########################################################
        # Expected sectors
        ##########################################################

        expected_s1 = median(sector1)
        expected_s2 = median(sector2)
        expected_s3 = median(sector3)

        ##########################################################
        # Actual sectors
        ##########################################################

        actual_s1 = lap.sector1_time.total_seconds()
        actual_s2 = lap.sector2_time.total_seconds()
        actual_s3 = lap.sector3_time.total_seconds()

        ##########################################################
        # Delta
        ##########################################################

        delta_s1 = actual_s1 - expected_s1
        delta_s2 = actual_s2 - expected_s2
        delta_s3 = actual_s3 - expected_s3

        ##########################################################
        # Score
        ##########################################################

        score = self._calculate_score(

            delta_s1,
            delta_s2,
            delta_s3

        )

        ##########################################################

        return SectorConsistency(

            expected_sector1=expected_s1,
            actual_sector1=actual_s1,
            delta_sector1=delta_s1,

            expected_sector2=expected_s2,
            actual_sector2=actual_s2,
            delta_sector2=delta_s2,

            expected_sector3=expected_s3,
            actual_sector3=actual_s3,
            delta_sector3=delta_s3,

            score=score,

            representative=(
                score >= self.REPRESENTATIVE_THRESHOLD
            )
        )

    ##############################################################

    def _calculate_score(
        self,
        delta_s1: float,
        delta_s2: float,
        delta_s3: float,
    ) -> int:

        total_delta = (

            abs(delta_s1)

            + abs(delta_s2)

            + abs(delta_s3)

        )

        penalty = total_delta * 25

        score = round(

            100 - penalty

        )

        return max(
            0,
            min(
                100,
                score
            )
        )