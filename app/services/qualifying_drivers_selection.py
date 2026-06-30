import fastf1
import pandas as pd

from app.services.team_normalizer import (
    normalize_team_name
)


def generate_driver_selection(
    year: int,
    round_number: int
) -> dict:

    # =====================================
    # Load Qualifying Session
    # =====================================

    quali_session = fastf1.get_session(
        year,
        round_number,
        "Q"
    )

    quali_session.load()

    # =====================================
    # Response
    # =====================================

    response = {
        "year": year,

        "round": round_number,

        "raceName": quali_session.event["EventName"],

        "sessions": {
            "Q1": [],
            "Q2": [],
            "Q3": []
        }
    }

    # =====================================
    # Build Driver Lists
    # =====================================

    for _, row in quali_session.results.iterrows():

        driver = {
            "driverCode": row["Abbreviation"],

            "driverLastName": row["LastName"],

            "teamName": normalize_team_name(
                row["TeamName"]
            ),

            "teamColor": row["TeamColor"],

            "position": int(row["Position"])
        }

        #
        # Every driver with a Q1 lap appears in Q1
        #
        if pd.notna(row["Q1"]):
            response["sessions"]["Q1"].append(
                driver.copy()
            )

        #
        # Drivers reaching Q2
        #
        if pd.notna(row["Q2"]):
            response["sessions"]["Q2"].append(
                driver.copy()
            )

        #
        # Drivers reaching Q3
        #
        if pd.notna(row["Q3"]):
            response["sessions"]["Q3"].append(
                driver.copy()
            )

    # =====================================
    # Sort By Qualifying Position
    # =====================================

    for session in response["sessions"].values():

        session.sort(
            key=lambda driver: driver["position"]
        )

    return response