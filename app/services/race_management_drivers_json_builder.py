from app.services.team_normalizer import (
    normalize_team_name,
)
from app.services.race_management.tyre_compound_service import (
    TyreCompoundService,
)


class RaceManagementDriversJsonBuilder:

    """
    Builds the Race Management driver selection JSON directly
    from the FastF1 session.
    """

    def __init__(self):

        self.tyre_compound_service = (
            TyreCompoundService()
        )
    
    ##############################################################

    def build(
        self,
        *,
        year,
        round_number,
        session,
    ):

        ##########################################################
        # Total race laps
        ##########################################################

        total_race_laps = int(

            session.results["Laps"].max()

        )
        
        ##########################################################
        # Tyre compounds used in this race
        ##########################################################

        tyre_compounds = []

        seen = set()

        for _, row in session.results.iterrows():

            driver_laps = session.laps.pick_drivers(

                row["DriverNumber"]

            )

            for _, stint_df in driver_laps.groupby(

                "Stint"

            ):

                compound = (

                    self.tyre_compound_service.normalize(

                        stint_df.iloc[0]["Compound"]

                    )

                )

                if (
                    compound
                    and compound not in seen
                ):

                    seen.add(compound)

                    tyre_compounds.append(

                        compound

                    )

        ##########################################################

        return {

            "year": year,

            "round": round_number,

            "totalRaceLaps": total_race_laps,
            
            "tyreCompounds": tyre_compounds,

            "drivers": [

                self._driver_json(

                    row,

                    session,

                )

                for _, row in session.results.iterrows()

            ],

        }

    ##############################################################

    def _driver_json(
        self,
        row,
        session,
    ):

        ##########################################################
        # Driver laps
        ##########################################################

        driver_number = row["DriverNumber"]

        driver_laps = session.laps.pick_drivers(

            driver_number

        )
        
        ##########################################################
        # Build stints
        ##########################################################

        stints = [

            self._stint_json(
                stint_df
            )

            for _, stint_df

            in driver_laps.groupby(
                "Stint"
            )

        ]

        ##########################################################
        # Fix missing opening laps in older FastF1 data
        ##########################################################

        if stints:

            first_recorded_lap = 1

            if (

                stints[0]["startLap"]

                > first_recorded_lap

            ):

                stints[0]["startLap"] = (

                    first_recorded_lap

                )

                stints[0]["lapCount"] = (

                    stints[0]["endLap"]

                    - stints[0]["startLap"]

                    + 1

                )


        ##########################################################

        return {

            "driverNumber": (
                driver_number
            ),

            "driverCode": (
                row["Abbreviation"]
            ),

            "firstName": (
                row["FirstName"]
            ),

            "lastName": (
                row["LastName"]
            ),

            "fullName": (
                row["FullName"]
            ),

            "team": normalize_team_name(

                row["TeamName"]

            ),

            "teamColor": (
                row["TeamColor"]
            ),

            "gridPosition": int(
                row["GridPosition"]
            ),

            "finishPosition": int(
                row["Position"]
            ),

            "status": (
                row["Status"]
            ),

            "lapsCompleted": int(
                row["Laps"]
            ),

            "stints": stints,

        }

    ##############################################################

    def _stint_json(
        self,
        stint_df,
    ):

        ##########################################################

        start_lap = int(

            stint_df["LapNumber"].min()

        )

        end_lap = int(

            stint_df["LapNumber"].max()

        )

        ##########################################################

        raw_compound = (

            stint_df.iloc[0]["Compound"]

        )

        ##########################################################

        return {

            "stint": int(

                stint_df.iloc[0]["Stint"]

            ),

            "compound": (

                self.tyre_compound_service.normalize(

                    raw_compound

                )

            ),

            "freshTyre": bool(

                stint_df.iloc[0]["FreshTyre"]

            ),

            "startLap": start_lap,

            "endLap": end_lap,

            "lapCount": (

                end_lap
                - start_lap
                + 1

            ),

        }