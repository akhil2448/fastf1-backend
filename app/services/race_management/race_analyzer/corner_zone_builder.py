from __future__ import annotations

from typing import Any


class CornerZoneBuilder:
    """
    Builds reusable corner zones from FastF1 circuit information.
    """

    #
    # Default distance before the apex.
    #
    ENTRY_DISTANCE = 70.0

    #
    # Default distance after the apex.
    #
    EXIT_DISTANCE = 70.0

    @classmethod
    def build(
        cls,
        session,
    ) -> list[dict[str, Any]]:

        circuit = session.get_circuit_info()

        corners = (
            circuit.corners
            .sort_values("Distance")
            .reset_index(drop=True)
        )

        zones = []

        for index, corner in corners.iterrows():

            apex = float(corner["Distance"])

            #
            # Distance to previous apex.
            #
            if index == 0:
                left_width = cls.ENTRY_DISTANCE
            else:
                previous_apex = float(
                    corners.iloc[index - 1]["Distance"]
                )

                left_width = min(
                    cls.ENTRY_DISTANCE,
                    (apex - previous_apex) / 2,
                )

            #
            # Distance to next apex.
            #
            if index == len(corners) - 1:
                right_width = cls.EXIT_DISTANCE
            else:
                next_apex = float(
                    corners.iloc[index + 1]["Distance"]
                )

                right_width = min(
                    cls.EXIT_DISTANCE,
                    (next_apex - apex) / 2,
                )

            zones.append(
                {
                    "corners": [
                        {
                            "number": int(corner["Number"]),
                            "letter": (
                                ""
                                if corner["Letter"] is None
                                else str(corner["Letter"])
                            ),
                            "apexDistance": round(apex, 3),
                        }
                    ],
                    "startDistance": round(
                        max(0.0, apex - left_width),
                        3,
                    ),
                    "endDistance": round(
                        apex + right_width,
                        3,
                    ),
                }
            )

        return cls._merge_touching(zones)

    @classmethod
    def _merge_touching(
        cls,
        zones: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        if not zones:
            return []

        merged = [zones[0]]

        for zone in zones[1:]:

            previous = merged[-1]

            #
            # Touching or overlapping zones
            # belong to one corner complex.
            #
            if (
                zone["startDistance"]
                <= previous["endDistance"]
            ):

                previous["corners"].extend(
                    zone["corners"]
                )

                previous["endDistance"] = max(
                    previous["endDistance"],
                    zone["endDistance"],
                )

            else:
                merged.append(zone)

        return merged