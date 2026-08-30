class AnalysisWindowService:

    DEFAULT_WINDOW_SIZE = 7

    @classmethod
    def prepare_stint(
        cls,
        stint_laps,
    ):
        """
        Prepare reusable analysis-window data for one stint.

        Returns:
            valid_laps
            lap_number -> index
        """

        valid_laps = [
            candidate
            for candidate in stint_laps
            if candidate.analysis.valid
        ]

        index_by_lap = {
            candidate.lap_number: index
            for index, candidate in enumerate(
                valid_laps
            )
        }

        return (
            valid_laps,
            index_by_lap,
        )

    @classmethod
    def build_window(
        cls,
        lap,
        stint_laps,
        window_size: int | None = None,
    ):

        valid_laps, index_by_lap = (
            cls.prepare_stint(
                stint_laps
            )
        )

        current_index = index_by_lap[
            lap.lap_number
        ]

        return cls.build_window_from_valid_laps(
            current_index,
            valid_laps,
            window_size,
        )

    @classmethod
    def build_window_from_valid_laps(
        cls,
        current_index: int,
        valid_laps,
        window_size: int | None = None,
    ):

        if window_size is None:
            window_size = cls.DEFAULT_WINDOW_SIZE

        half = window_size // 2

        start = current_index - half
        end = current_index + half + 1

        if start < 0:

            end += -start
            start = 0

        if end > len(valid_laps):

            start -= end - len(valid_laps)
            end = len(valid_laps)

        start = max(
            0,
            start,
        )

        return valid_laps[start:end]