# from dataclasses import dataclass, field


# @dataclass
# class LapPairRecommendation:
#     """
#     Represents one recommended lap comparison between two drivers.
#     """

#     driver_a_lap: int
#     driver_b_lap: int

#     driver_a_tyre_age: int
#     driver_b_tyre_age: int

#     driver_a_compound: str
#     driver_b_compound: str

#     compatibility_score: int

#     reasons: list[str] = field(default_factory=list)


from dataclasses import dataclass, field

from .models import AnalyzedLap


@dataclass
class LapPairRecommendation:
    """
    Represents one recommended lap comparison between two drivers.
    """

    lap_a: AnalyzedLap
    lap_b: AnalyzedLap

    compatibility_score: int

    reasons: list[str] = field(default_factory=list)