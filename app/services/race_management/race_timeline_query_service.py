from .models import (
    DriverLapTimeline,
    RaceTimeline,
)


class RaceTimelineQueryService:
    """
    Performs fast queries on an already-built RaceTimeline.
    """

    ##############################################################

    def get_driver_lap(
        self,
        timeline: RaceTimeline,
        driver_number: str,
        session_time,
    ) -> DriverLapTimeline | None:

        driver = timeline.drivers.get(
            driver_number
        )

        if driver is None:
            return None

        for lap in driver.laps:

            if (
                lap.lap_start_time
                <= session_time
                <= lap.lap_end_time
            ):
                return lap

        return None

    ##############################################################

    def get_drivers_on_lap(
        self,
        timeline: RaceTimeline,
        lap_number: int,
        session_time,
    ) -> list[str]:

        drivers = []

        for driver_number in timeline.drivers:

            lap = self.get_driver_lap(
                timeline,
                driver_number,
                session_time,
            )

            if lap is None:
                continue

            if lap.lap_number == lap_number:

                drivers.append(
                    driver_number
                )

        return drivers