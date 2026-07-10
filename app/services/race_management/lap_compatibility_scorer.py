class LapCompatibilityScorer:
    """
    Calculates how comparable two laps are.

    100 = Nearly identical conditions
      0 = Poor comparison
    """
    
    COMPOUND_PENALTY = 40

    TYRE_AGE_PENALTY = 5

    REPRESENTATIVE_WEIGHT = 0.20
    TRAFFIC_WEIGHT = 0.10

    ##############################################################

    def score(
        self,
        recommendation,
    ) -> int:

        score = 100

        ##########################################################
        # Tyre compound
        ##########################################################

        if (
            recommendation.lap_a.normalized_compound
            != recommendation.lap_b.normalized_compound
        ):

            score -= self.COMPOUND_PENALTY

        ##########################################################
        # Tyre age
        ##########################################################

        tyre_age_delta = abs(

            recommendation.lap_a.tyre_life
            - recommendation.lap_b.tyre_life

        )

        score -= tyre_age_delta * self.TYRE_AGE_PENALTY
        
        ##########################################################
        # Representative quality
        ##########################################################

        representative_score = (

            recommendation.lap_a.representative.overall_score

            + recommendation.lap_b.representative.overall_score

        ) / 2

        score -= (

            (100 - representative_score)

            * self.REPRESENTATIVE_WEIGHT

        )
        
        ##########################################################
        # Traffic quality
        ##########################################################

        traffic_score = (

            recommendation.lap_a.traffic.traffic_score

            + recommendation.lap_b.traffic.traffic_score

        ) / 2

        score -= (

            (100 - traffic_score)

            * self.TRAFFIC_WEIGHT

        )

        ##########################################################

        return max(
            0,
            min(
                100,
                score,
            ),
        )