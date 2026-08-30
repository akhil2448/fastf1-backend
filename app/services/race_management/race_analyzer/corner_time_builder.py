from __future__ import annotations

from typing import Any

import pandas as pd


class CornerTimeBuilder:
    """
    Calculates how much lap time was spent
    inside the official circuit corner zones.
    """

    @classmethod
    def build(
        cls,
        telemetry: pd.DataFrame,
        corner_zones: list[dict[str, Any]],
    ) -> dict[str, Any]:

        if telemetry.empty or not corner_zones:
            return {
                "lapTime": 0.0,
                "cornerTime": 0.0,
                "cornerPercentage": 0.0,
                "zones": [],
            }

        lap_time = telemetry.iloc[-1]["Time"].total_seconds()

        total_corner_time = 0.0

        zone_results = []

        for zone in corner_zones:

            zone_time = cls._calculate_zone_time(
                telemetry,
                zone,
            )

            total_corner_time += zone_time

            zone_results.append(
                {
                    "corners": zone["corners"],
                    "startDistance": zone["startDistance"],
                    "endDistance": zone["endDistance"],
                    "time": round(zone_time, 3),
                }
            )

        return {
            "lapTime": round(lap_time, 3),
            "cornerTime": round(total_corner_time, 3),
            "cornerPercentage": round(
                total_corner_time / lap_time * 100,
                2,
            ) if lap_time > 0 else 0.0,
            "zones": zone_results,
        }

    @classmethod
    def _calculate_zone_time(
        cls,
        telemetry: pd.DataFrame,
        zone: dict[str, Any],
    ) -> float:

        start_time = cls._interpolate_time_at_distance(
            telemetry,
            zone["startDistance"],
        )

        end_time = cls._interpolate_time_at_distance(
            telemetry,
            zone["endDistance"],
        )

        if (
            start_time is None
            or end_time is None
            or end_time <= start_time
        ):
            return 0.0

        return end_time - start_time

    @classmethod
    def _interpolate_time_at_distance(
        cls,
        telemetry: pd.DataFrame,
        target_distance: float,
    ) -> float | None:

        distances = telemetry["Distance"].to_numpy()
        times = telemetry["Time"]

        if len(distances) == 0:
            return None

        #
        # Find the first telemetry sample whose distance
        # is greater than or equal to the target.
        #
        index = distances.searchsorted(
            target_distance,
            side="left",
        )

        #
        # Target is beyond the final telemetry sample.
        # Preserve the existing behavior for a corner zone
        # extending past the finish line.
        #
        if index >= len(distances):
            return times.iloc[-1].total_seconds()

        #
        # Target is before or exactly at the first sample.
        #
        if index == 0:

            if distances[0] == target_distance:
                return times.iloc[0].total_seconds()

            return None

        d1 = float(distances[index - 1])
        d2 = float(distances[index])

        t1 = times.iloc[index - 1].total_seconds()
        t2 = times.iloc[index].total_seconds()

        #
        # Exact distance match.
        #
        if d2 == target_distance:
            return t2

        #
        # Preserve the existing zero-distance behavior.
        #
        if d2 == d1:
            return t1

        #
        # Linear interpolation between the two surrounding
        # telemetry samples.
        #
        ratio = (
            target_distance - d1
        ) / (
            d2 - d1
        )

        return t1 + ratio * (t2 - t1)