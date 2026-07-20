class RaceGapCalculator:
    """
    Calculates the gap between two cars around the race circuit.

    Positive gap:
        Other driver is ahead.

    Negative gap:
        Other driver is behind.

    Unit:
        Laps (floating point)
    """

    ##############################################################

    def calculate_gap(
        self,
        current_lap: int,
        current_progress: float,
        other_lap: int,
        other_progress: float,
    ) -> float:

        ##########################################################
        # Whole lap difference
        ##########################################################

        lap_gap = other_lap - current_lap

        ##########################################################
        # Fractional progress
        ##########################################################

        progress_gap = (
            other_progress
            - current_progress
        )

        ##########################################################

        return lap_gap + progress_gap