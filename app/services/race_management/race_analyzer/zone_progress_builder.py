from __future__ import annotations

from typing import Any


class ZoneProgressBuilder:
    """
    Determines how each driving phase relates
    to the nearest official corner zone.

    This builder does not classify lift-and-coast.
    It simply describes the phase's relationship
    to the corner.
    """

    @classmethod
    def build(
        cls,
        phases: list[dict[str, Any]],
        corner_zones: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        results = []

        for phase in phases:

            zone = cls._find_zone(
                phase,
                corner_zones,
            )

            if zone is None:
                continue

            phase_start = phase["startDistance"]
            phase_end = phase["endDistance"]

            zone_start = zone["startDistance"]
            zone_end = zone["endDistance"]

            #
            # Relationship between this driving phase
            # and the corner zone.
            #
            if phase_end < zone_start:

                relationship = "BEFORE"

            elif (
                phase_start < zone_start
                and phase_end <= zone_end
            ):

                relationship = "ENTERS"

            elif (
                zone_start <= phase_start
                and phase_end <= zone_end
            ):

                relationship = "INSIDE"

            elif (
                zone_start <= phase_start <= zone_end
                and phase_end > zone_end
            ):

                relationship = "EXITS"

            elif (
                phase_start < zone_start
                and phase_end > zone_end
            ):

                relationship = "CROSSES"

            else:

                relationship = "AFTER"

            #
            # Progress when phase begins.
            #
            if phase_start <= zone_start:

                entry_progress = 0.0

            elif phase_start >= zone_end:

                entry_progress = 100.0

            else:

                entry_progress = (
                    (phase_start - zone_start)
                    /
                    (zone_end - zone_start)
                    * 100
                )

            #
            # Progress when phase ends.
            #
            if phase_end <= zone_start:

                exit_progress = 0.0

            elif phase_end >= zone_end:

                exit_progress = 100.0

            else:

                exit_progress = (
                    (phase_end - zone_start)
                    /
                    (zone_end - zone_start)
                    * 100
                )

            results.append(
                {
                    "phase": phase["phase"],

                    "startTime": phase["startTime"],
                    "endTime": phase["endTime"],

                    "startDistance": phase["startDistance"],
                    "endDistance": phase["endDistance"],

                    "zone": zone,

                    "relationship": relationship,

                    "distanceToEntry": round(
                        max(
                            0.0,
                            zone_start - phase_start,
                        ),
                        2,
                    ),

                    "distanceToExit": round(
                        max(
                            0.0,
                            phase_start - zone_end,
                        ),
                        2,
                    ),

                    "entryProgress": round(
                        entry_progress,
                        1,
                    ),

                    "exitProgress": round(
                        exit_progress,
                        1,
                    ),
                }
            )

        return results

    @classmethod
    def _find_zone(
        cls,
        phase: dict[str, Any],
        corner_zones: list[dict[str, Any]],
    ):

        phase_start = phase["startDistance"]
        phase_end = phase["endDistance"]

        #
        # Find the zone with the greatest overlap.
        #
        best_zone = None
        largest_overlap = 0.0

        for zone in corner_zones:

            zone_start = zone["startDistance"]
            zone_end = zone["endDistance"]

            overlap = (
                min(phase_end, zone_end)
                -
                max(phase_start, zone_start)
            )

            if overlap > largest_overlap:

                largest_overlap = overlap
                best_zone = zone

        #
        # If we overlap a corner, use that corner.
        #
        if best_zone is not None:
            return best_zone

        #
        # Otherwise return the nearest corner.
        #
        nearest = None
        shortest = float("inf")

        midpoint = (
            phase_start
            + phase_end
        ) / 2

        for zone in corner_zones:

            zone_start = zone["startDistance"]
            zone_end = zone["endDistance"]

            if midpoint < zone_start:
                distance = zone_start - midpoint
            else:
                distance = midpoint - zone_end

            if distance < shortest:

                shortest = distance
                nearest = zone

        return nearest