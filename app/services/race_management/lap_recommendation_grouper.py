from .lap_recommendation_group import (
    LapRecommendationGroup,
)


class LapRecommendationGrouper:
    """
    Groups lap recommendations by the secondary driver's lap.

    Multiple primary-driver laps may recommend the same
    secondary-driver lap.
    """

    ##############################################################

    def group(
        self,
        recommendations,
    ):

        groups = {}

        ##########################################################
        # Group by secondary lap
        ##########################################################

        for recommendation in recommendations:

            key = (
                recommendation.lap_b.stint,
                recommendation.lap_b.lap_number,
            )

            if key not in groups:

                groups[key] = (

                    LapRecommendationGroup(

                        secondary_lap=(
                            recommendation.lap_b
                        ),

                    )

                )

            groups[
                key
            ].recommendations.append(
                recommendation
            )

        ##########################################################

        return list(
            groups.values()
        )