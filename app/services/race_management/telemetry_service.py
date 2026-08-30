from .models import (
    TelemetryFrame,
    TelemetrySample,
)

import pandas as pd


class TelemetryService:
    """
    Converts FastF1 telemetry into PitWall's canonical
    telemetry model.

    Every future analyzer uses this instead of directly
    reading FastF1 telemetry.
    """

    def build(
        self,
        session,
        driver_number: str,
    ) -> TelemetryFrame:

        frame = TelemetryFrame(
            driver_number=driver_number,
        )

        driver_laps = session.laps.pick_drivers(
            driver_number
        )

        ##########################################################
        # Process every lap
        ##########################################################

        for _, lap in driver_laps.iterrows():

            ######################################################
            # Ignore invalid laps
            ######################################################

            if lap["LapTime"] is pd.NaT:
                continue

            ######################################################
            # Load telemetry
            ######################################################

            telemetry = (
                lap
                .get_car_data()
                .add_distance()
            )

            if telemetry.empty:
                continue

            ######################################################
            # Extract columns once.
            #
            # This avoids DataFrame.iterrows(), which creates a
            # pandas Series object for every telemetry sample.
            ######################################################

            session_times = (
                telemetry["SessionTime"].tolist()
            )

            distances = (
                telemetry["Distance"].to_numpy()
            )

            speeds = (
                telemetry["Speed"].to_numpy()
            )

            rpms = (
                telemetry["RPM"].to_numpy()
            )

            throttles = (
                telemetry["Throttle"].to_numpy()
            )

            brakes = (
                telemetry["Brake"].to_numpy()
            )

            gears = (
                telemetry["nGear"].to_numpy()
            )

            drs_values = (
                telemetry["DRS"].to_numpy()
            )

            max_distance = telemetry[
                "Distance"
            ].max()

            lap_number = int(
                lap["LapNumber"]
            )

            ######################################################

            for index in range(
                len(telemetry)
            ):

                distance = distances[index]

                ##################################################
                # Preserve existing NaN distance behavior.
                ##################################################

                if distance != distance:
                    continue

                speed = speeds[index]

                ##################################################
                # Preserve existing stationary sample behavior.
                ##################################################

                if speed < 5:
                    continue

                ##################################################

                frame.samples.append(

                    TelemetrySample(

                        session_time=(
                            session_times[index]
                        ),

                        lap_number=lap_number,

                        distance=float(
                            distance
                        ),

                        normalized_distance=(
                            float(distance)
                            / max_distance
                        ),

                        speed=float(
                            speed
                        ),

                        rpm=float(
                            rpms[index]
                        ),

                        throttle=float(
                            throttles[index]
                        ),

                        brake=bool(
                            brakes[index]
                        ),

                        gear=int(
                            gears[index]
                        ),

                        drs=int(
                            drs_values[index]
                        ),
                    )
                )

        return frame