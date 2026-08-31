from app.services.race_management.models import (
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

            max_distance = telemetry["Distance"].max()

            ######################################################

            for _, row in telemetry.iterrows():

                distance = row["Distance"]

                ######################################################
                # Skip invalid distance
                ######################################################

                if distance != distance:
                    continue

                ######################################################
                # Ignore stationary / almost stationary samples
                ######################################################

                if row["Speed"] < 5:
                    continue

                ######################################################

                frame.samples.append(

                    TelemetrySample(

                        session_time=row["SessionTime"],

                        lap_number=int(
                            lap["LapNumber"]
                        ),

                        distance=float(distance),

                        normalized_distance=(
                            float(distance)
                            / max_distance
                        ),

                        speed=float(row["Speed"]),

                        rpm=float(row["RPM"]),

                        throttle=float(
                            row["Throttle"]
                        ),

                        brake=bool(row["Brake"]),

                        gear=int(row["nGear"]),

                        drs=int(row["DRS"]),
                    )
                )

        return frame