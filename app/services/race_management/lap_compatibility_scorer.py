class LapCompatibilityScorer:
    """
    Calculates how comparable two laps are.

    Final score is a weighted average of:

    Representative Quality : 40%
    Tyre State             : 25%
    Race Phase             : 20%
    Traffic / Wake         : 10%
    Lap Time Similarity    : 5%
    """

    REPRESENTATIVE_WEIGHT = 0.40
    TYRE_WEIGHT = 0.25
    RACE_PHASE_WEIGHT = 0.20
    TRAFFIC_WEIGHT = 0.10
    LAP_TIME_WEIGHT = 0.05

    ##############################################################

    def score(
        self,
        recommendation,
    ) -> int:

        representative = self._representative_score(
            recommendation
        )

        tyre = self._tyre_score(
            recommendation
        )

        race_phase = self._race_phase_score(
            recommendation
        )

        traffic = self._traffic_score(
            recommendation
        )

        lap_time = self._lap_time_score(
            recommendation
        )

        score = (

            representative * self.REPRESENTATIVE_WEIGHT

            + tyre * self.TYRE_WEIGHT

            + race_phase * self.RACE_PHASE_WEIGHT

            + traffic * self.TRAFFIC_WEIGHT

            + lap_time * self.LAP_TIME_WEIGHT

        )

        return round(score)
    
    
    def _representative_score(
        self,
        recommendation,
    ):

        return (

            recommendation.lap_a.representative.overall_score

            + recommendation.lap_b.representative.overall_score

        ) / 2
        
    def _tyre_score(
        self,
        recommendation,
    ):

        score = 100

        ##########################################################
        # Compound
        ##########################################################

        if (
            recommendation.lap_a.normalized_compound
            != recommendation.lap_b.normalized_compound
        ):

            score -= 40

        ##########################################################
        # Tyre age
        ##########################################################

        tyre_delta = abs(

            recommendation.lap_a.tyre_life
            - recommendation.lap_b.tyre_life

        )

        score -= tyre_delta * 5

        return max(0, score)
    
    
    def _race_phase_score(
        self,
        recommendation,
    ):

        lap_delta = abs(

            recommendation.lap_a.lap_number

            - recommendation.lap_b.lap_number

        )

        score = 100 - lap_delta * 5

        return max(0, score)
    
    
    
    def _traffic_score(
        self,
        recommendation,
    ):

        return (

            recommendation.lap_a.traffic.traffic_score

            + recommendation.lap_b.traffic.traffic_score

        ) / 2
        
        
    def _lap_time_score(
        self,
        recommendation,
    ):

        delta = abs(

            recommendation.lap_a.representative.lap_time.delta_seconds

            - recommendation.lap_b.representative.lap_time.delta_seconds

        )

        score = 100 - delta * 25

        return max(0, score)