from __future__ import annotations

from typing import Any

import pandas as pd


class RaceMetadataBuilder:
    """
    Builds race-level metadata for the Race Analyzer.

    All lap numbers are relative to the reference driver.
    """

    @classmethod
    def build(
        cls,
        session,
        reference_driver: str,
    ) -> dict[str, Any]:

        reference_laps = (
            session.laps
            .pick_drivers(reference_driver)
            .copy()
        )

        return {
            "statusRanges": cls._build_status_ranges(
                session=session,
                reference_laps=reference_laps,
            ),

            "rainRanges": cls._build_rain_ranges(
                session=session,
                reference_laps=reference_laps,
            ),
        }

    # ==========================================================
    # Track Status
    # ==========================================================

    @classmethod
    def _build_status_ranges(
        cls,
        session,
        reference_laps: pd.DataFrame,
    ) -> list[dict[str, Any]]:

        events = []

        for _, row in session.track_status.iterrows():

            lap_number = cls._find_reference_driver_lap(
                reference_laps=reference_laps,
                session_time=row["Time"],
            )

            if lap_number is None:
                continue

            for digit in str(row["Status"]):

                events.append(
                    {
                        "lap": lap_number,
                        "status": cls._status_name(int(digit)),
                        "time": str(row["Time"]),
                    }
                )

        return events

    # ==========================================================
    # Rain
    # ==========================================================

    @classmethod
    def _build_rain_ranges(
        cls,
        session,
        reference_laps: pd.DataFrame,
    ) -> list[dict[str, Any]]:

        #
        # Build from session.weather_data
        #
        return []

    # ==========================================================
    # Helpers
    # ==========================================================

    @classmethod
    def _find_reference_driver_lap(
        cls,
        reference_laps: pd.DataFrame,
        session_time,
    ) -> int | None:

        for _, lap in reference_laps.iterrows():

            lap_start = lap["LapStartTime"]
            lap_end = lap["Time"]

            if (
                pd.notna(lap_start)
                and pd.notna(lap_end)
                and lap_start <= session_time < lap_end
            ):
                return int(lap["LapNumber"])

        return None

    @classmethod
    def _decode_track_status(
        cls,
        track_status: int,
    ) -> list[int]:
        """
        Example:

        1   -> [1]
        124 -> [1, 2, 4]
        125 -> [1, 2, 5]
        167 -> [1, 6, 7]
        """

        return [
            int(ch)
            for ch in str(track_status)
        ]

    @classmethod
    def _persistent_track_status(
        cls,
        current_sequence: list[int],
        next_sequence: list[int] | None,
    ) -> int:
        """
        Determines the dominant (persistent) track status for a lap.

        Examples

        [1]       -> GREEN

        [4]       -> SAFETY CAR

        [1,2,4]   -> SAFETY CAR

        [4,5]     -> RED FLAG

        [1,6,7]
        next=[1,6]
                -> VSC

        [1,6,7]
        next=[1]
                -> GREEN
        """

        #
        # Simple lap
        #
        if len(current_sequence) == 1:
            return current_sequence[0]

        #
        # No following lap
        #
        if next_sequence is None:
            return current_sequence[-1]

        current_end = current_sequence[-1]

        next_start = next_sequence[0]

        #
        # Status continued into next lap.
        #
        if current_end == next_start:
            return current_end

        #
        # Transition finished before next lap.
        #
        return next_start

    @classmethod
    def _merge_ranges(
        cls,
        ranges: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Merge consecutive ranges having identical status.

        Will be implemented after status mapping.
        """
        return ranges

    @classmethod
    def _status_name(
        cls,
        status: int,
    ) -> str:

        return {
            1: "GREEN",
            2: "YELLOW",
            4: "SAFETY_CAR",
            5: "RED_FLAG",
            6: "VSC",
            7: "VSC_ENDING",
        }.get(status, "UNKNOWN")