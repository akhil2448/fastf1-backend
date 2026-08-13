from __future__ import annotations

import pandas as pd


class DrivingPhaseBuilder:

    @classmethod
    def build(
        cls,
        telemetry: pd.DataFrame,
    ) -> list[dict]:

        telemetry = telemetry.copy()

        telemetry["Phase"] = telemetry.apply(
            cls._classify_phase,
            axis=1,
        )

        segments = []

        current_phase = telemetry.iloc[0]["Phase"]
        start_index = 0

        for index in range(1, len(telemetry)):

            if telemetry.iloc[index]["Phase"] != current_phase:

                segments.append(
                    (
                        current_phase,
                        start_index,
                        index,
                    )
                )

                current_phase = telemetry.iloc[index]["Phase"]
                start_index = index

        segments.append(
            (
                current_phase,
                start_index,
                len(telemetry) - 1,
            )
        )

        phases = []

        for i, (phase, start_index, _) in enumerate(segments):

            if i < len(segments) - 1:
                end_index = segments[i + 1][1]
            else:
                end_index = len(telemetry) - 1

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
            "startDistance": round(start_distance, 3),
            "endDistance": round(end_distance, 3),
            "startTime": round(start_time, 3),
            "endTime": round(end_time, 3),
            "distance": round(end_distance - start_distance, 3),
            "duration": round(end_time - start_time, 3),
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