class LapComparisonReasonBuilder:

    """
    Builds human-readable explanations for why two laps
    are (or are not) good candidates for comparison.
    """

    ##########################################################

    def build(
        self,
        recommendation,
    ) -> list[str]:

        reasons = []

        ######################################################
        # Tyres
        ######################################################

        reason = self._build_tyre_reason(
            recommendation
        )

        if reason:
            reasons.append(reason)

        ######################################################
        # Race phase
        ######################################################

        # reason = self._build_race_phase_reason(
        #     recommendation
        # )

        # if reason:
        #     reasons.append(reason)

        ######################################################
        # Representative
        ######################################################

        reason = self._build_representative_reason(
            recommendation
        )

        if reason:
            reasons.append(reason)

        ######################################################
        # Traffic / Wake
        ######################################################

        reason = self._build_traffic_reason(
            recommendation
        )

        if reason:
            reasons.append(reason)

        ######################################################
        # Lap pace
        ######################################################

        # reason = self._build_lap_time_reason(
        #     recommendation
        # )

        # if reason:
        #     reasons.append(reason)

        return reasons

    ##########################################################

    def _build_tyre_reason(
        self,
        recommendation,
    ):

        lap_a = recommendation.lap_a
        lap_b = recommendation.lap_b
        
        driver_a = lap_a.driver_code
        driver_b = lap_b.driver_code

        ##########################################################
        # Compound
        ##########################################################

        if (
            lap_a.normalized_compound
            == lap_b.normalized_compound
        ):

            compound_text = (

                f"{driver_a} and {driver_b} both used "
                f"{lap_a.compound} tyres"

            )

        else:

            compound_text = (

                f"{driver_a} used {lap_a.compound} tyres "
                f"while {driver_b} used "
                f"{lap_b.compound}"

            )

        ##########################################################
        # Tyre age
        ##########################################################

        tyre_delta = abs(
            lap_a.tyre_life
            - lap_b.tyre_life
        )

        return (

            f"{compound_text}. "

            f"Tyre age differs by "
            f"{tyre_delta} lap"

            f"{'' if tyre_delta == 1 else 's'} "

            f"({lap_a.tyre_life} vs "
            f"{lap_b.tyre_life})."

        )

    ##########################################################

    def _build_race_phase_reason(
        self,
        recommendation,
    ):

        lap_a = recommendation.lap_a
        lap_b = recommendation.lap_b
        
        driver_a = lap_a.driver_code
        driver_b = lap_b.driver_code

        lap_delta = abs(

            lap_a.lap_number
            - lap_b.lap_number

        )

        ##########################################################
        # Same race lap
        ##########################################################

        if lap_delta == 0:

            return (

                f"{driver_a} and {driver_b} both completed "
                f"their laps on race lap "
                f"{lap_a.lap_number}."

            )

        ##########################################################
        # Different race laps
        ##########################################################

        return (

            f"{driver_a} completed lap "
            f"{lap_a.lap_number}, while "
            f"{driver_b} completed lap "
            f"{lap_b.lap_number} "
            f"({lap_delta} lap"
            f"{'' if lap_delta == 1 else 's'} apart)."

        )

    ##########################################################

    def _build_representative_reason(
        self,
        recommendation,
    ):

        lap_a = recommendation.lap_a
        lap_b = recommendation.lap_b
        
        driver_a = lap_a.driver_code
        driver_b = lap_b.driver_code

        representative_a = (
            lap_a.representative.overall_score
        )

        representative_b = (
            lap_b.representative.overall_score
        )

        ##########################################################
        # Both representative
        ##########################################################

        if (
            lap_a.representative.representative
            and
            lap_b.representative.representative
        ):

            return (

                f"Both laps closely match each driver's "
                f"expected race pace "
                f"({driver_a}: {representative_a}, "
                f"{driver_b}: {representative_b})."

            )

        ##########################################################
        # One representative
        ##########################################################

        if (
            lap_a.representative.representative
            !=
            lap_b.representative.representative
        ):

            better_driver = (

                driver_a

                if lap_a.representative.representative

                else driver_b

            )

            return (

                f"{better_driver} produced the more "
                f"representative lap "
                f"({driver_a}: {representative_a}, "
                f"{driver_b}: {representative_b})."

            )

        ##########################################################
        # Neither representative
        ##########################################################

        return (

            f"Neither lap perfectly matches the "
            f"expected race pace "
            f"({driver_a}: {representative_a}, "
            f"{driver_b}: {representative_b})."

        )

    ##########################################################

    def _build_traffic_reason(
        self,
        recommendation,
    ):

        lap_a = recommendation.lap_a
        lap_b = recommendation.lap_b

        traffic_a = lap_a.traffic
        traffic_b = lap_b.traffic

        driver_a = lap_a.driver_code
        driver_b = lap_b.driver_code

        clean_a = traffic_a.clean_air_percentage
        clean_b = traffic_b.clean_air_percentage

        description_a = self._traffic_description(
            clean_a
        )

        description_b = self._traffic_description(
            clean_b
        )

        ##########################################################
        # Similar conditions
        ##########################################################

        if description_a == description_b:

            return (

                f"Both drivers ran in "
                f"{description_a}."

            )

        ##########################################################
        # Different conditions
        ##########################################################

        return (

            f"{driver_a} ran in {description_a}, "
            f"while {driver_b} enjoyed "
            f"{description_b}."

        )
        
    
    ##########################################################

    def _traffic_description(
        self,
        clean_air_percentage,
    ):

        if clean_air_percentage >= 95:

            return "clean air"

        if clean_air_percentage >= 75:

            return "mostly clean air"

        if clean_air_percentage >= 50:

            return "light traffic"

        if clean_air_percentage >= 25:

            return "moderate traffic"

        return "heavy traffic"

    ##########################################################

    def _build_lap_time_reason(
        self,
        recommendation,
    ):

        lap_a = recommendation.lap_a
        lap_b = recommendation.lap_b

        driver_a = lap_a.driver_code
        driver_b = lap_b.driver_code

        delta_a = abs(
            lap_a.representative.lap_time.delta_seconds
        )

        delta_b = abs(
            lap_b.representative.lap_time.delta_seconds
        )

        ##########################################################
        # Both excellent
        ##########################################################

        if (
            delta_a <= 0.20
            and
            delta_b <= 0.20
        ):

            return (
                "Both laps closely matched the expected race pace."
            )

        ##########################################################
        # Both good
        ##########################################################

        if (
            delta_a <= 0.50
            and
            delta_b <= 0.50
        ):

            return (
                "Both laps were close to the expected race pace."
            )

        ##########################################################
        # One better
        ##########################################################

        better_driver = (
            driver_a
            if delta_a < delta_b
            else driver_b
        )

        return (
            f"{better_driver}'s lap was closer to the expected race pace."
        )
