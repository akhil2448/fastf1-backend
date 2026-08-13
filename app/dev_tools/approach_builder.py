from __future__ import annotations

from typing import Any

import math
import pandas as pd


class ApproachBuilder:
    """
    Associates each off-throttle driving phase with the
    nearest official circuit corner.

    This builder performs no lift-and-coast classification.
    It only exposes the geometric relationship between the
    car and the nearest corner apex.
    """

    OFF_THROTTLE_PHASES = {
        "ROLL",
        "LIFT",
    }

    @classmethod
    def build(
        cls,
        telemetry: pd.DataFrame,
        phases: list[dict[str, Any]],
        circuit_info,
    ) -> list[dict[str, Any]]:

        if telemetry.empty:
            return []

        results = []

        for phase in phases:

            if phase["phase"] not in cls.OFF_THROTTLE_PHASES:
                continue

            start_sample = telemetry.iloc[
                phase["startIndex"]
            ]

            end_sample = telemetry.iloc[
                phase["endIndex"]
            ]

            start_corner = cls._nearest_corner(
                float(start_sample["X"]),
                float(start_sample["Y"]),
                circuit_info,
            )

            end_corner = cls._nearest_corner(
                float(end_sample["X"]),
                float(end_sample["Y"]),
                circuit_info,
            )

            results.append(
                {
                    "phase": phase["phase"],

                    "startTime": phase["startTime"],
                    "endTime": phase["endTime"],

                    "startDistance": phase["startDistance"],
                    "endDistance": phase["endDistance"],

                    "startCorner": start_corner,
                    "endCorner": end_corner,
                }
            )

        return results

    @classmethod
    def _nearest_corner(
        cls,
        x: float,
        y: float,
        circuit_info,
    ) -> dict[str, Any]:

        nearest = None

        shortest_distance = float("inf")

        for _, corner in circuit_info.corners.iterrows():

            dx = x - float(corner["X"])
            dy = y - float(corner["Y"])

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if distance < shortest_distance:

                shortest_distance = distance

                nearest = {
                    "number": int(
                        corner["Number"]
                    ),
                    "letter": str(
                        corner["Letter"]
                    ),
                    "distance": round(
                        distance,
                        2,
                    ),
                    "x": float(corner["X"]),
                    "y": float(corner["Y"]),
                }

        return nearest
