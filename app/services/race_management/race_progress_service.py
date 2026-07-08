from .models import (
    TelemetryFrame,
    RaceProgressFrame,
    RaceProgressSample,
)


class RaceProgressService:

    """
    Builds normalized race progress from FastF1 telemetry.

    Unlike TrackProgressService, this service uses telemetry
    Distance instead of X/Y coordinates.
    """

    def build(
        self,
        telemetry: TelemetryFrame,
    ) -> RaceProgressFrame:

        frame = RaceProgressFrame(
            driver_number=telemetry.driver_number,
        )

        ##########################################################
        # Copy canonical telemetry into race progress samples
        ##########################################################

        for sample in telemetry.samples:

            frame.samples.append(

                RaceProgressSample(

                    session_time=sample.session_time,

                    lap_number=sample.lap_number,

                    distance=sample.distance,

                    normalized_progress=(
                        sample.normalized_distance
                    ),

                    speed=sample.speed,
                    drs=sample.drs,
                )
            )

        return frame