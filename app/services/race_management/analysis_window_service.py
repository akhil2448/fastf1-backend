class AnalysisWindowService:

    DEFAULT_WINDOW_SIZE = 7

    def build_window(
        self,
        lap,
        stint_laps,
        window_size: int | None = None,
    ):

        if window_size is None:
            window_size = self.DEFAULT_WINDOW_SIZE

        ##########################################################
        # Valid laps only
        ##########################################################

        valid_laps = [
            candidate
            for candidate in stint_laps
            if candidate.analysis.valid
        ]

        ##########################################################
        # Find current lap
        ##########################################################

        current_index = next(

            index

            for index, candidate in enumerate(valid_laps)

            if candidate.lap_number == lap.lap_number

        )

        ##########################################################
        # Initial window
        ##########################################################

        half = window_size // 2

        start = current_index - half
        end = current_index + half + 1

        ##########################################################
        # Shift left/right to keep full window
        ##########################################################

        if start < 0:

            end += -start
            start = 0

        if end > len(valid_laps):

            start -= end - len(valid_laps)
            end = len(valid_laps)

        start = max(0, start)

        ##########################################################

        return valid_laps[start:end]