from datetime import timedelta

from .models import (
    RaceTimeline,
    DriverTimeline,
    DriverLapTimeline,
)


class RaceTimelineService:
    """
    Builds lap-by-lap timing information for every driver.
    """

    def build(
        self,
        session,
    ) -> RaceTimeline:

        timeline = RaceTimeline()

        ##########################################################

        for driver_number in session.drivers:

            driver_laps = session.laps.pick_drivers(
                driver_number
            )

            driver_timeline = DriverTimeline(
                driver_number=driver_number,
            )

            cumulative = timedelta()

            ######################################################

            for _, lap in driver_laps.iterrows():

                if lap["LapTime"] is None:
                    continue

                if lap["LapTime"] != lap["LapTime"]:
                    continue

                lap_time = lap["LapTime"]

                lap_end = lap["Time"]

                lap_start = lap_end - lap_time

                cumulative += lap_time

                lap_timeline = DriverLapTimeline(

                    lap_number=int(
                        lap["LapNumber"]
                    ),

                    lap_start_time=lap_start,

                    lap_end_time=lap_end,

                    lap_time=lap_time,

                    cumulative_time=cumulative,
                )

                driver_timeline.laps.append(
                    lap_timeline
                )

                driver_timeline.laps_by_number[
                    lap_timeline.lap_number
                ] = lap_timeline

            ######################################################

            timeline.drivers[
                driver_number
            ] = driver_timeline

        ##########################################################

        return timeline