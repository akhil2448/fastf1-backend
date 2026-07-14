from app.services.team_normalizer import normalize_team_name


class LapComparisonJsonBuilder:
    """
    Converts lap comparison recommendations into a frontend-ready JSON
    response.
    """

    ##############################################################

    def build(
        self,
        *,
        year,
        round_number,
        driver_a,
        driver_b,
        stint_comparisons,
        driver_code_lookup,
    ):

        return {

            "year": year,

            "round": round_number,

            "driverA": self._driver_json(
                driver_a
            ),

            "driverB": self._driver_json(
                driver_b
            ),

            "stintComparisons": [

                self._stint_json(

                    comparison,

                    driver_code_lookup,

                )

                for comparison in stint_comparisons

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
        comparison,
        driver_code_lookup,
    ):

        return {

            "driverAStint": (
                comparison.driver_a_stint
            ),

            "driverBStint": (
                comparison.driver_b_stint
            ),

            "compoundA": (
                comparison.compound_a
            ),

            "compoundB": (
                comparison.compound_b
            ),

           "recommendationGroups": [

                self._group_json(

                    group,

                    driver_code_lookup,

                )

                for group in comparison.groups

            ],

        }

    ##############################################################

    def _group_json(
        self,
        group,
        driver_code_lookup,
    ):

        return {

            "secondaryLap": (
                group.secondary_lap.lap_number
            ),

            "recommendations": [

                self._recommendation_json(

                    recommendation,

                    driver_code_lookup,

                )

                for recommendation in (
                    group.recommendations
                )

            ],

        }

    ##############################################################

    def _recommendation_json(
        self,
        recommendation,
        driver_code_lookup,
    ):

        return {

            "compatibilityScore": (
                recommendation
                .compatibility_score
            ),

            "lapA": self._lap_json(

                recommendation.lap_a,
                driver_code_lookup,

            ),

            "lapB": self._lap_json(

                recommendation.lap_b,
                driver_code_lookup,

            ),

            "reasons": (
                recommendation.reasons
            ),
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

            "representative": {

                "score": (
                    lap.representative
                    .overall_score
                ),

                "representative": (
                    lap.representative
                    .representative
                ),

                ######################################################
                # Lap Time
                ######################################################

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

                ######################################################
                # Sector
                ######################################################

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

                ######################################################
                # Position
                ######################################################

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

                ######################################################
                # Traffic
                ######################################################

                "traffic": {

                    "score": (
                        lap.representative
                        .traffic.traffic_score
                    ),

                },

            },

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

                "averageFollowingGapDistance": (

                    None

                    if lap.traffic.average_gap_ahead_distance is None

                    else round(

                        lap.traffic.average_gap_ahead_distance,

                        1,

                    )

                ),

                "closestFollowingGapDistance": (

                    None

                    if lap.traffic.minimum_gap_ahead_distance is None

                    else round(

                        lap.traffic.minimum_gap_ahead_distance,

                        1,

                    )

                ),

            },
            
            ######################################################
            # DRS
            ######################################################

            "drs": {

                "nearestCarAhead": (

                    driver_code_lookup.get(

                        lap.traffic.nearest_car_ahead

                    )

                ),

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

            },

        }