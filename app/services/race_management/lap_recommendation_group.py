from dataclasses import dataclass, field

from .models import AnalyzedLap
from .lap_pair_recommendation import (
    LapPairRecommendation,
)


@dataclass
class LapRecommendationGroup:
    """
    Groups multiple lap recommendations that all
    point to the same secondary-driver lap.
    """

    secondary_lap: AnalyzedLap

    recommendations: list[LapPairRecommendation] = field(
        default_factory=list
    )