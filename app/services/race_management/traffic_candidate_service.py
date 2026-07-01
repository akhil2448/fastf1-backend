from .models import RaceTimeline
from .race_timeline_query_service import (
    RaceTimelineQueryService,
)


class TrafficCandidateService:
    """
    Returns the small subset of drivers that could realistically
    influence traffic for a given driver.

    Phase 1:
        Same lap
        Previous lap
        Next lap
    """

    def __init__(self):

        self.timeline_query = (
            RaceTimelineQueryService()
        )

    ##############################################################

    def get_candidates(
        self,
        timeline: RaceTimeline,
        driver_number: str,
        session_time,
    ) -> list[str]:

        current_lap = self.timeline_query.get_driver_lap(
            timeline,
            driver_number,
            session_time,
        )

        if current_lap is None:
            return []

        candidates = []

        ##########################################################

        for other_driver in timeline.drivers:

            if other_driver == driver_number:
                continue

            other_lap = self.timeline_query.get_driver_lap(
                timeline,
                other_driver,
                session_time,
            )

            if other_lap is None:
                continue

            ######################################################

            if abs(
                other_lap.lap_number
                - current_lap.lap_number
            ) <= 1:

                candidates.append(
                    other_driver
                )

        ##########################################################

        return candidates