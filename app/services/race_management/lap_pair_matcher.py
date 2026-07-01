from .lap_pair_recommendation import LapPairRecommendation


class LapPairMatcher:

    # Maximum tyre age difference we'll consider.
    # We can tune this later.
    MAX_TYRE_AGE_DELTA = 3

    def match(self, driver_a_stint, driver_b_stint):

        recommendations = []

        valid_a = [
            lap
            for lap in driver_a_stint.analyzed_laps
            if lap.analysis.valid
        ]

        valid_b = [
            lap
            for lap in driver_b_stint.analyzed_laps
            if lap.analysis.valid
        ]

        for lap_a in valid_a:

            best_match = self._find_best_match(
                lap_a,
                valid_b
            )

            if best_match is None:
                continue

            recommendations.append(

                LapPairRecommendation(

                    driver_a_lap=lap_a.lap_number,

                    driver_b_lap=best_match.lap_number,

                    driver_a_tyre_age=lap_a.tyre_life,

                    driver_b_tyre_age=best_match.tyre_life,

                    driver_a_compound=lap_a.compound,

                    driver_b_compound=best_match.compound,

                    compatibility_score=0,

                    reasons=[]
                )
            )

        return recommendations

    ###############################################################

    def _find_best_match(
        self,
        lap_a,
        candidate_laps
    ):

        best = None
        best_distance = None

        for lap_b in candidate_laps:

            tyre_age_delta = abs(
                lap_a.tyre_life -
                lap_b.tyre_life
            )

            if tyre_age_delta > self.MAX_TYRE_AGE_DELTA:
                continue

            race_lap_delta = abs(
                lap_a.lap_number -
                lap_b.lap_number
            )

            distance = (
                tyre_age_delta * 100
                + race_lap_delta
            )

            if best is None or distance < best_distance:

                best = lap_b
                best_distance = distance

        return best