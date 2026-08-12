from __future__ import annotations

from typing import Any

import pandas as pd


class RaceMetadataBuilder:
    """
    Builds race-level metadata for the Race Analyzer.

    All lap numbers are relative to the reference driver.
    """
    
    _STATUS_SEVERITY = {
        1: 0,
        7: 0,
        2: 1,
        6: 2,
        4: 3,
        5: 4,
    }

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

        events = cls._build_status_events(
            session=session,
            reference_laps=reference_laps,
        )

        return cls._build_status_ranges_from_events(
            events=events,
            reference_laps=reference_laps,
        )
        
    
    @classmethod
    def _build_status_events(
        cls,
        session,
        reference_laps: pd.DataFrame,
    ) -> list[dict[str, Any]]:

        events = []

        for _, row in session.track_status.iterrows():

            events.append(
                {
                    "lap": cls._find_reference_driver_lap(
                        reference_laps,
                        row["Time"],
                    ),
                    "sessionTime": round(
                        row["Time"].total_seconds(),
                        3,
                    ),
                    "status": int(row["Status"]),
                }
            )

        return events
    
    @classmethod
    def _build_status_ranges_from_events(
        cls,
        events: list[dict[str, Any]],
        reference_laps: pd.DataFrame,
    ) -> list[dict[str, Any]]:

        #
        # Final status assigned to each reference-driver lap.
        #
        lap_status: dict[int, int] = {}

        #
        # Group all track-status events by the
        # reference driver's lap.
        #
        events_by_lap: dict[int, list[dict[str, Any]]] = {}

        for event in events:

            if event["lap"] is None:
                continue

            events_by_lap.setdefault(
                event["lap"],
                []
            ).append(event)

        active_status = 1

        last_lap = int(
            reference_laps["LapNumber"].max()
        )

        for lap in range(1, last_lap + 1):

            #
            # Determine the status to display for
            # this lap before processing new events.
            #
            if active_status == 5:
                display_status = 1
            else:
                display_status = active_status

            #
            # Apply every status transition that
            # occurred during this lap.
            #
            for event in events_by_lap.get(lap, []):

                status = event["status"]

                if status not in (1, 2, 4, 5, 6, 7):
                    continue

                #
                # Highest severity seen during THIS LAP.
                #
                if (
                    cls._STATUS_SEVERITY[status]
                    > cls._STATUS_SEVERITY[display_status]
                ):
                    display_status = status

                #
                # Determine the status carried into
                # the next reference-driver lap.
                #
                if status in (1, 7):
                    active_status = 1

                #
                # Safety Car and VSC continue until cancelled.
                #
                elif status in (4, 6):
                    active_status = status

                #
                # Red Flag only paints the current lap.
                #
                elif status == 5:
                    active_status = 1

                #
                # Yellow lasts until replaced.
                #
                elif status == 2:
                    active_status = 2

            lap_status[lap] = display_status

        #
        # Compress consecutive laps.
        #
        ranges = []

        current_status = None
        start_lap = None
        previous_lap = None

        for lap in sorted(lap_status.keys()):

            status = lap_status[lap]

            #
            # Skip green laps.
            #
            if status == 1:

                if current_status is not None:
                    ranges.append({
                        "status": cls._status_name(current_status),
                        "startLap": start_lap,
                        "endLap": previous_lap,
                    })

                    current_status = None

                previous_lap = lap
                continue

            if current_status is None:

                current_status = status
                start_lap = lap

            elif status != current_status:

                ranges.append({
                    "status": cls._status_name(current_status),
                    "startLap": start_lap,
                    "endLap": previous_lap,
                })

                current_status = status
                start_lap = lap

            previous_lap = lap

        if current_status is not None:

            ranges.append({
                "status": cls._status_name(current_status),
                "startLap": start_lap,
                "endLap": previous_lap,
            })

        return ranges
    
    # ==========================================================
    # Rain
    # ==========================================================

    @classmethod
    def _build_rain_ranges(
        cls,
        session,
        reference_laps: pd.DataFrame,
    ) -> list[dict[str, Any]]:

        events = cls._build_rain_events(
            session=session,
            reference_laps=reference_laps,
        )

        return cls._compress_rain_events(events)
    

    @classmethod
    def _build_rain_events(
        cls,
        session,
        reference_laps: pd.DataFrame,
    ) -> list[dict[str, Any]]:

        events = []

        for _, row in session.weather_data.iterrows():

            if not row["Rainfall"]:
                continue

            lap = cls._find_reference_driver_lap(
                reference_laps,
                row["Time"],
            )

            if lap is None:
                continue

            events.append(
                {
                    "lap": lap,
                }
            )

        return events
    
    
    @classmethod
    def _compress_rain_events(
        cls,
        events: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        if not events:
            return []

        #
        # Remove duplicate laps.
        #
        laps = sorted(
            {
                event["lap"]
                for event in events
            }
        )

        ranges = []

        start = laps[0]
        previous = laps[0]

        for lap in laps[1:]:

            if lap == previous + 1:
                previous = lap
                continue

            ranges.append(
                {
                    "startLap": start,
                    "endLap": previous,
                }
            )

            start = lap
            previous = lap

        ranges.append(
            {
                "startLap": start,
                "endLap": previous,
            }
        )

        return ranges

    # ==========================================================
    # Helpers
    # ==========================================================

    @classmethod
    def _find_reference_driver_lap(
        cls,
        reference_laps: pd.DataFrame,
        session_time,
    ) -> int | None:

        #
        # Event occurred during a lap.
        #
        for _, lap in reference_laps.iterrows():

            lap_start = lap["LapStartTime"]
            lap_end = lap["Time"]

            if (
                pd.notna(lap_start)
                and pd.notna(lap_end)
                and lap_start <= session_time <= lap_end
            ):
                return int(lap["LapNumber"])

        #
        # Event occurred between two completed laps.
        # Assign it to the next lap.
        #
        previous_end = None

        for _, lap in reference_laps.iterrows():

            lap_start = lap["LapStartTime"]

            if (
                previous_end is not None
                and previous_end < session_time < lap_start
            ):
                return int(lap["LapNumber"])

            if pd.notna(lap["Time"]):
                previous_end = lap["Time"]

        #
        # Event happened after the driver's final lap.
        #
        return None

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
            7: "VSC_END",
        }.get(status, "UNKNOWN")