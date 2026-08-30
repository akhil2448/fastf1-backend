from __future__ import annotations

import numpy as np
import pandas as pd


class DrivingPhaseBuilder:

    @classmethod
    def build(
        cls,
        telemetry: pd.DataFrame,
    ) -> list[dict]:

        telemetry = telemetry.copy()

        # ------------------------------------------------------
        # Vectorized phase classification.
        #
        # This preserves the exact priority of the original
        # _classify_phase() implementation:
        #
        #   BRAKE
        #   ROLL
        #   LIFT
        #   FULL
        #   PART
        #
        # but avoids telemetry.apply(axis=1), which creates a
        # pandas Series and invokes Python code for every row.
        # ------------------------------------------------------

        brake = telemetry["Brake"].astype(bool)
        throttle = telemetry["Throttle"]

        telemetry["Phase"] = np.select(
            [
                brake,
                throttle <= 5,
                throttle <= 20,
                throttle == 100,
            ],
            [
                "BRAKE",
                "ROLL",
                "LIFT",
                "FULL",
            ],
            default="PART",
        )

        # ------------------------------------------------------
        # Read phase values directly instead of repeatedly using
        # telemetry.iloc[index]["Phase"].
        # ------------------------------------------------------

        phase_values = telemetry["Phase"].to_numpy()

        segments = []

        current_phase = phase_values[0]
        start_index = 0

        for index in range(1, len(phase_values)):

            if phase_values[index] != current_phase:

                segments.append(
                    (
                        current_phase,
                        start_index,
                        index,
                    )
                )

                current_phase = phase_values[index]
                start_index = index

        segments.append(
            (
                current_phase,
                start_index,
                len(phase_values) - 1,
            )
        )

        phases = []

        for i, (phase, start_index, _) in enumerate(segments):

            if i < len(segments) - 1:
                end_index = segments[i + 1][1]
            else:
                end_index = len(phase_values) - 1

            phases.append(
                cls._create_phase(
                    telemetry,
                    phase,
                    start_index,
                    end_index,
                )
            )

        return phases

    @classmethod
    def _create_phase(
        cls,
        telemetry: pd.DataFrame,
        phase: str,
        start_index: int,
        end_index: int,
    ) -> dict:

        start = telemetry.iloc[start_index]
        end = telemetry.iloc[end_index]

        start_distance = float(start["Distance"])
        end_distance = float(end["Distance"])

        start_time = start["Time"].total_seconds()
        end_time = end["Time"].total_seconds()

        return {
            "phase": phase,

            #
            # Original telemetry indices.
            #
            "startIndex": start_index,
            "endIndex": end_index,

            "startDistance": round(start_distance, 3),
            "endDistance": round(end_distance, 3),

            "startTime": round(start_time, 3),
            "endTime": round(end_time, 3),

            "distance": round(
                end_distance - start_distance,
                3,
            ),

            "duration": round(
                end_time - start_time,
                3,
            ),
        }

    @classmethod
    def _classify_phase(
        cls,
        row,
    ) -> str:

        throttle = row["Throttle"]
        brake = row["Brake"]

        if brake:
            return "BRAKE"

        #
        # Rolling
        #
        if throttle <= 5:
            return "ROLL"

        #
        # Lift
        #
        if throttle <= 20:
            return "LIFT"

        #
        # Full throttle
        #
        if throttle == 100:
            return "FULL"

        #
        # Partial throttle
        #
        return "PART"