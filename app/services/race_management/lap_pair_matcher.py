from .lap_pair_recommendation import LapPairRecommendation
from .tyre_compound_service import TyreCompoundService

class LapPairMatcher:
    
    def __init__(self):
        self.compound_service = TyreCompoundService()

    # Maximum tyre age difference we'll consider.
    # We can tune this later.
    MAX_WEAR_PERCENTAGE_DELTA = 0.12
    MAX_RACE_LAP_DELTA = 8
    WEAR_PERCENTAGE_WEIGHT = 100
    LAP_WEIGHT = 1

    def match(self, driver_a_stint, driver_b_stint):

        recommendations = []

        valid_a = [
            lap
            for lap in driver_a_stint.analyzed_laps
            if (
                lap.analysis.valid
                and lap.representative
                and lap.representative.representative
            )
        ]

        valid_b = [
            lap
            for lap in driver_b_stint.analyzed_laps
            if (
                lap.analysis.valid
                and lap.representative
                and lap.representative.representative
            )
        ]

        for lap_a in valid_a:

            best_matches = self._find_best_matches(
                lap_a,
                valid_b,
            )

            for match in best_matches:

                recommendations.append(

                    LapPairRecommendation(

                        lap_a=lap_a,

                        lap_b=match,

                        compatibility_score=0,

                        reasons=[],
                    )

                )

        return recommendations

    ###############################################################

    def _find_best_matches(
        self,
        lap_a,
        candidate_laps,
    ):

        same_compound = []

        different_compound = []

        for lap_b in candidate_laps:

            wear_a = (

                lap_a.tyre_life

                / self.compound_service.reference_life(
                    lap_a.normalized_compound
                )

            )

            wear_b = (

                lap_b.tyre_life

                / self.compound_service.reference_life(
                    lap_b.normalized_compound
                )

            )

            wear_delta = abs(

                wear_a -
                wear_b

            )

            if wear_delta > self.MAX_WEAR_PERCENTAGE_DELTA:
                continue

            race_lap_delta = abs(
                lap_a.lap_number -
                lap_b.lap_number
            )

            if race_lap_delta > self.MAX_RACE_LAP_DELTA:
                continue

            distance = (

                wear_delta * self.WEAR_PERCENTAGE_WEIGHT

                + race_lap_delta * self.LAP_WEIGHT

            )

            candidate = (
                distance,
                lap_b,
            )

            if (
                lap_a.normalized_compound
                == lap_b.normalized_compound
            ):
                same_compound.append(candidate)

            else:
                different_compound.append(candidate)

        candidates = (
            same_compound
            if same_compound
            else different_compound
        )

        candidates.sort(
            key=lambda candidate: candidate[0]
        )

        return [
            lap
            for _, lap in candidates[:3]
        ]