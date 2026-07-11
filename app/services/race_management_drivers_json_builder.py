from app.services.team_normalizer import (
    normalize_team_name,
)


class RaceManagementDriversJsonBuilder:

    """
    Builds the Race Management driver selection JSON directly
    from the FastF1 session.
    """

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

        return {

            "year": year,

            "round": round_number,

            "totalRaceLaps": total_race_laps,

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

            "stints": [

                self._stint_json(
                    stint_df
                )

                for _, stint_df

                in driver_laps.groupby(
                    "Stint"
                )

            ],

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

        return {

            "stint": int(

                stint_df.iloc[0]["Stint"]

            ),

            "compound": (

                stint_df.iloc[0]["Compound"]

            ),

            "startLap": start_lap,

            "endLap": end_lap,

            "lapCount": (

                end_lap

                - start_lap

                + 1

            ),

        }