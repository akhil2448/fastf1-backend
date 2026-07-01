from app.services.race_management.race_management_service import (
    RaceManagementService,
)
from app.services.race_management.lap_pair_matcher import (
    LapPairMatcher,
)

YEAR = 2024
ROUND = 11


def main():

    service = RaceManagementService()
    matcher = LapPairMatcher()

    drivers = service.analyze_race(
        YEAR,
        ROUND,
    )

    ham = next(d for d in drivers if d.driver_code == "HAM")
    ver = next(d for d in drivers if d.driver_code == "VER")

    stint_a = ham.stints[1]      # Hard stint
    stint_b = ver.stints[1]      # Hard stint

    recommendations = matcher.match(
        stint_a,
        stint_b,
    )

    print()

    print(f"HAM Stint {stint_a.stint}")
    print(f"VER Stint {stint_b.stint}")

    print()

    print(f"Recommendations : {len(recommendations)}")

    print()

    for recommendation in recommendations:

        print(
            f"HAM Lap {recommendation.driver_a_lap:>2}"
            f" (Age {recommendation.driver_a_tyre_age:>2})"
            "  <-->  "
            f"VER Lap {recommendation.driver_b_lap:>2}"
            f" (Age {recommendation.driver_b_tyre_age:>2})"
        )


if __name__ == "__main__":
    main()