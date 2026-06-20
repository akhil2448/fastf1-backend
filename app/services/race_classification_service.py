# services/race_classification_service.py

from __future__ import annotations
import fastf1

# from fastf1 import api
from fastf1.ergast import Ergast
import pandas as pd

from typing import Dict, Any, List

from app.services.team_normalizer import (
    normalize_team_name
)


class RaceClassificationService:

    def build_classification(
        self,
        year: int,
        round_number: int
    ) -> Dict[str, Any]:

        session = fastf1.get_session(year, round_number, "R")
        session.load()
        ergast = Ergast()
        # driver_info_map = fastf1.api.driver_info(
        #     session.api_path
        # )

        results = session.results
        laps_df = session.laps

        classification: List[Dict[str, Any]] = []

        total_laps = int(results["Laps"].max())
        
        # -------------------------------------------------
        # DRIVER CHAMPIONSHIP STANDINGS
        # -------------------------------------------------

        driver_standings_response = ergast.get_driver_standings(
            season=year,
            round=round_number
        )

        driver_standings_df = (
            driver_standings_response.content[0]
        )

        driver_standings: List[Dict[str, Any]] = []

        for _, row in (
            driver_standings_df.head(10).iterrows()
        ):

            constructor_names = row.get(
                "constructorNames",
                []
            )

            team_name = normalize_team_name(
                constructor_names[0]
            ) if constructor_names else ""

            driver_standings.append({
                "position": int(row["position"]),

                "driver": row["givenName"]
                + " "
                + row["familyName"],

                "driverCode": row["driverCode"],

                "team": team_name,

                "points": float(row["points"]),
            })
            
        # -------------------------------------------------
        # CONSTRUCTOR CHAMPIONSHIP STANDINGS
        # -------------------------------------------------

        constructor_standings_response = (
            ergast.get_constructor_standings(
                season=year,
                round=round_number
            )
        )

        constructor_standings_df = (
            constructor_standings_response.content[0]
        )

        constructor_standings: List[Dict[str, Any]] = []

        for _, row in (
            constructor_standings_df.iterrows()
        ):

            normalized_team = normalize_team_name(
                row["constructorName"]
            )

            constructor_standings.append({
                "position": int(row["position"]),

                "teamName": normalized_team,

                "team": normalized_team,

                "points": float(row["points"]),
            })
            
        
        # -------------------------------------------------
        # FASTEST LAP
        # -------------------------------------------------

        fastest_lap = session.laps.pick_fastest()

        fastest_lap_driver = (
            fastest_lap["Driver"]
        )

        fastest_lap_time = (
            fastest_lap["LapTime"]
        )

        fastest_lap_number = int(
            fastest_lap["LapNumber"]
        )

        fastest_lap_driver_result = (
            results[
                results["Abbreviation"]
                == fastest_lap_driver
            ].iloc[0]
        )

        fastest_lap_full_name = (
            fastest_lap_driver_result["FullName"]
        )

        fastest_lap_team = normalize_team_name(
            fastest_lap_driver_result["TeamName"]
        )

        fastest_lap_time_seconds = (
            fastest_lap_time.total_seconds()
        )

        minutes = int(
            fastest_lap_time_seconds // 60
        )

        seconds = (
            fastest_lap_time_seconds % 60
        )

        formatted_fastest_lap = (
            f"{minutes}:{seconds:06.3f}"
        )

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

            full_name = row["FullName"]

            driver_number = str(row["DriverNumber"])

            team_name = normalize_team_name(row["TeamName"])
            
            # -------------------------------------------------
            # DRIVER COUNTRY
            # -------------------------------------------------

            # driver_data = driver_info_map.get(driver_number)

            # country_code = None

            # if driver_data:

            #     country_code = (
            #         driver_data.get("CountryCode", "")
            #         .strip()
            #         .lower()
            #     )

            # print(driver, country_code)
            
            position = int(row["Position"])

            laps_completed = int(row["Laps"])

            status_text = str(row["Status"])

            points = float(row["Points"])

            driver_laps = laps_df.pick_drivers(driver)

            # -------------------------------------------------
            # DETERMINE DRIVER STATUS
            # -------------------------------------------------

            classified_position = str(
                row["ClassifiedPosition"]
            ).strip()

            if classified_position.isdigit():
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

            # if finish_time is not None:

            #     race_end_time = max(
            #         race_end_time,
            #         finish_time
            #     )

            # -------------------------------------------------
            # DISPLAY GAP
            # -------------------------------------------------

            display_gap = None

            # Winner
            if position == 1:

                display_gap = "WINNER"

            # Same-lap finishers
            elif gap_to_leader is not None:

                # Under 1 minute
                if gap_to_leader < 60:

                    display_gap = f"+{gap_to_leader:.3f}"

                # 1 minute or more
                else:

                    minutes = int(gap_to_leader // 60)

                    seconds = gap_to_leader % 60

                    display_gap = (
                        f"+{minutes}:{seconds:06.3f}"
                    )

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

                "fullName": full_name,

                "driverNumber": driver_number,

                "team": team_name,
                
                # "countryCode": country_code,

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

            # "raceEndTime": race_end_time,

            "totalLaps": total_laps,

            "classification": classification,
            
            "driverStandings": driver_standings,

            "constructorStandings": constructor_standings,
            
            "fastestLap": {
                "driver": fastest_lap_driver,

                "fullName": fastest_lap_full_name,

                "team": fastest_lap_team,

                "lapNumber": fastest_lap_number,

                "lapTime": formatted_fastest_lap,
            },
        }