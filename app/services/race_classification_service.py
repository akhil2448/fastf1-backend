# services/race_classification_service.py

from __future__ import annotations

import fastf1
import pandas as pd

from typing import Dict, Any, List


class RaceClassificationService:

    def build_classification(
        self,
        year: int,
        round_number: int
    ) -> Dict[str, Any]:

        session = fastf1.get_session(year, round_number, "R")
        session.load()

        results = session.results
        laps_df = session.laps

        classification: List[Dict[str, Any]] = []

        total_laps = int(results["Laps"].max())

        # -------------------------------------------------
        # WINNER ABSOLUTE FINISH TIME
        # -------------------------------------------------

        winner_row = results.iloc[0]

        winner_finish_time = (
            winner_row["Time"].total_seconds()
        )

        race_end_time = winner_finish_time

        # -------------------------------------------------
        # BUILD CLASSIFICATION
        # -------------------------------------------------

        for _, row in results.iterrows():

            driver = row["Abbreviation"]

            position = int(row["Position"])

            laps_completed = int(row["Laps"])

            status_text = str(row["Status"])

            points = float(row["Points"])

            driver_laps = laps_df.pick_drivers(driver)

            # -------------------------------------------------
            # DETERMINE DRIVER STATUS
            # -------------------------------------------------

            if "Finished" in status_text or "+" in status_text:
                status = "FINISHED"
            else:
                status = "OUT"

            # -------------------------------------------------
            # GAP TO LEADER
            # -------------------------------------------------

            gap_to_leader = None

            # Winner
            if position == 1:
                gap_to_leader = 0

            # Same-lap classified finishers
            elif (
                pd.notna(row["Time"])
                and laps_completed == total_laps
            ):
                gap_to_leader = (
                    row["Time"].total_seconds()
                )

            # -------------------------------------------------
            # ABSOLUTE FINISH TIME
            # -------------------------------------------------

            finish_time = None

            # Winner
            if position == 1:

                finish_time = winner_finish_time

            # Same-lap classified finishers
            elif gap_to_leader is not None:

                finish_time = (
                    winner_finish_time
                    + gap_to_leader
                )

            # Lapped classified finishers
            elif (
                status == "FINISHED"
                and not driver_laps.empty
            ):

                last_lap = driver_laps.iloc[-1]

                lap_start = last_lap["LapStartTime"]

                lap_time = last_lap["LapTime"]

                if (
                    pd.notna(lap_start)
                    and pd.notna(lap_time)
                ):
                    finish_time = (
                        lap_start.total_seconds()
                        + lap_time.total_seconds()
                    )

            # -------------------------------------------------
            # LAPS DOWN
            # -------------------------------------------------

            laps_down = max(
                0,
                total_laps - laps_completed
            )

            # -------------------------------------------------
            # TRACK TRUE RACE END TIME
            # -------------------------------------------------

            if finish_time is not None:

                race_end_time = max(
                    race_end_time,
                    finish_time
                )

            # -------------------------------------------------
            # DISPLAY GAP
            # -------------------------------------------------

            display_gap = None

            # Winner
            if position == 1:

                display_gap = "WINNER"

            # Same-lap finishers
            elif gap_to_leader is not None:

                display_gap = f"+{gap_to_leader:.3f}"

            # Lapped finishers
            elif laps_down > 0:

                if laps_down == 1:
                    display_gap = "+1 LAP"
                else:
                    display_gap = f"+{laps_down} LAPS"

            # Retired cars
            else:

                display_gap = status_text

            # -------------------------------------------------
            # CLASSIFICATION ENTRY
            # -------------------------------------------------

            classification.append({
                "driver": driver,

                "position": position,

                "status": status,

                "statusText": status_text,

                "displayGap": display_gap,

                "finishTime": finish_time,

                "gapToLeader": gap_to_leader,

                "lapsCompleted": laps_completed,

                "lapsDown": laps_down,

                "points": points,
            })

        # -------------------------------------------------
        # FINAL PAYLOAD
        # -------------------------------------------------

        return {
            "winnerFinishTime": winner_finish_time,

            "raceEndTime": race_end_time,

            "totalLaps": total_laps,

            "classification": classification,
        }