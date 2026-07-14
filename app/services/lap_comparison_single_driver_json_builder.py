from app.services.team_normalizer import normalize_team_name


class LapComparisonSingleDriverJsonBuilder:
    """
    Converts a single driver's analyzed laps into a frontend-ready JSON
    response.
    """

    ##############################################################

    def build(
        self,
        *,
        year,
        round_number,
        driver,
        driver_code_lookup,
    ):

        return {

            "year": year,

            "round": round_number,

            "driver": self._driver_json(
                driver
            ),

            "stints": [

                self._stint_json(

                    stint,

                    driver_code_lookup,

                )

                for stint in driver.stints

            ],

        }

    ##############################################################

    def _driver_json(
        self,
        driver,
    ):

        names = (
            driver.full_name.split(
                maxsplit=1
            )
        )

        first_name = names[0]

        last_name = (
            names[1]
            if len(names) > 1
            else ""
        )

        return {

            "driverNumber": (
                driver.driver_number
            ),

            "driverCode": (
                driver.driver_code
            ),

            "firstName": first_name,

            "lastName": last_name,

            "fullName": (
                driver.full_name
            ),

            "team": normalize_team_name(
                driver.team_name
            ),

            "teamColor": (
                driver.team_color
            ),
        }

    ##############################################################

    def _stint_json(
        self,
        stint,
        driver_code_lookup,
    ):

        return {

            "stint": (
                stint.stint
            ),

            "compound": (
                stint.compound
            ),

            "lapCount": len(
                stint.analyzed_laps
            ),

            "laps": [

                self._lap_json(

                    lap,

                    driver_code_lookup,

                )

                for lap in stint.analyzed_laps

            ],

        }

    ##############################################################

    def _lap_json(
        self,
        lap,
        driver_code_lookup,
    ):

        return {

            "lapNumber": (
                lap.lap_number
            ),

            "position": (
                lap.position
            ),

            "compound": (
                lap.compound
            ),

            "tyreAge": (
                lap.tyre_life
            ),

            "lapTimeSeconds": round(

                lap.lap_time.total_seconds(),

                3,

            ),

            ######################################################
            # Representative
            ######################################################

            "representative": {

                "score": (
                    lap.representative
                    .overall_score
                ),

                "representative": (
                    lap.representative
                    .representative
                ),

                "lapTime": {

                    "score": (
                        lap.representative
                        .lap_time.score
                    ),

                    "deltaSeconds": round(

                        lap.representative
                        .lap_time.delta_seconds,

                        3,

                    ),

                },

                "sector": {

                    "score": (
                        lap.representative
                        .sector.score
                    ),

                    "sector1Delta": round(

                        lap.representative
                        .sector.delta_sector1,

                        3,

                    ),

                    "sector2Delta": round(

                        lap.representative
                        .sector.delta_sector2,

                        3,

                    ),

                    "sector3Delta": round(

                        lap.representative
                        .sector.delta_sector3,

                        3,

                    ),

                },

                "position": {

                    "score": (
                        lap.representative
                        .position.score
                    ),

                    "deltaPosition": (
                        lap.representative
                        .position.delta_position
                    ),

                },

                "traffic": {

                    "score": (
                        lap.representative
                        .traffic.traffic_score
                    ),

                },

            },

            ######################################################
            # Traffic
            ######################################################

            "traffic": {

                "score": (
                    lap.traffic
                    .traffic_score
                ),

                "cleanAirPercentage": round(

                    lap.traffic
                    .clean_air_percentage,

                    1,

                ),

                "timeInDirtyAir": round(

                    lap.traffic
                    .time_in_dirty_air,

                    1,

                ),

                "weightedDirtyAir": round(

                    lap.traffic
                    .dirty_air_percentage,

                    1,

                ),

                ##################################################
                # Wake
                ##################################################

                "averageWakePercentage": round(

                    lap.traffic
                    .average_wake_strength
                    * 100,

                    1,

                ),

                "maximumWakePercentage": round(

                    lap.traffic
                    .maximum_wake_strength
                    * 100,

                    1,

                ),

                ##################################################
                # Following distance
                ##################################################

                "averageFollowingGapDistance": (

                    None

                    if lap.traffic.average_gap_ahead_distance is None

                    else round(

                        lap.traffic
                        .average_gap_ahead_distance,

                        1,

                    )

                ),

                "closestFollowingGapDistance": (

                    None

                    if lap.traffic.minimum_gap_ahead_distance is None

                    else round(

                        lap.traffic
                        .minimum_gap_ahead_distance,

                        1,

                    )

                ),

            },
            
            ######################################################
            # DRS
            ######################################################

            "drs": {

                "drsUsagePercentage": round(

                    lap.traffic
                    .drs_percentage,

                    1,

                ),

                "drsWhileFollowingPercentage": round(

                    lap.traffic
                    .drs_in_dirty_air_percentage,

                    1,

                ),

                "nearestCarAhead": (

                    driver_code_lookup.get(

                        lap.traffic
                        .nearest_car_ahead

                    )

                ),

            },

            ######################################################
            # Human-readable reasons
            ######################################################

            "reasons": (

                lap.representative.reasons

            ),

        }