from .lap_pair_matcher import LapPairMatcher
from .lap_compatibility_scorer import LapCompatibilityScorer
from .lap_comparison_reason_builder import (
    LapComparisonReasonBuilder,
)
from .lap_recommendation_grouper import (
    LapRecommendationGrouper,
)


class LapComparisonService:
    """
    Finds the best comparable laps between two drivers.

    Flow

    Driver A stint
            +
    Driver B stint
            ↓
      Candidate Matching
            ↓
    Compatibility Scoring
            ↓
      Reason Generation
            ↓
    Recommended Lap Pairs
    """
    
    MIN_COMPATIBILITY_SCORE = 85

    def __init__(self):

        self.matcher = LapPairMatcher()

        self.scorer = LapCompatibilityScorer()

        self.reason_builder = (
            LapComparisonReasonBuilder()
        )
        
        self.grouper = (
            LapRecommendationGrouper()
        )

    ##############################################################

    def compare(
        self,
        driver_a_stint,
        driver_b_stint,
    ):

        ##########################################################
        # Find candidate lap pairs
        ##########################################################

        recommendations = self.matcher.match(

            driver_a_stint,
            driver_b_stint,
        )

        ##########################################################
        # Score every recommendation
        ##########################################################

        for recommendation in recommendations:

            recommendation.compatibility_score = (

                self.scorer.score(
                    recommendation
                )

            )

            ######################################################
            # Reasons
            ######################################################

            recommendation.reasons = (

                self.reason_builder.build(
                    recommendation
                )

            )

        ##########################################################
        
        recommendations = [

            recommendation

            for recommendation in recommendations

            if (
                recommendation.compatibility_score
                >= self.MIN_COMPATIBILITY_SCORE
            )

        ]
        
        ##########################################################
        # Group recommendations
        ##########################################################

        groups = self.grouper.group(
            recommendations
        )
        
        ##########################################################
        # Sort recommendations inside every group
        ##########################################################

        for group in groups:

            group.recommendations.sort(

                key=lambda recommendation: (
                    recommendation.compatibility_score
                ),

                reverse=True,

            )
            
        ##########################################################
        # Sort groups
        ##########################################################

        groups.sort(

            key=lambda group: (

                group.recommendations[0]
                .compatibility_score

            ),

            reverse=True,

        )

        ##########################################################

        return groups