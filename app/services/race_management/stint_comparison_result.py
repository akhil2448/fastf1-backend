from dataclasses import dataclass

from .lap_recommendation_group import (
    LapRecommendationGroup,
)


@dataclass
class StintComparisonResult:

    driver_a_stint: int
    driver_b_stint: int
    compound_a: str
    compound_b: str
    groups: list[LapRecommendationGroup]