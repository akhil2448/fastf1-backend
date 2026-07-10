from app.services.race_management.race_management_service import (
    RaceManagementService,
)

from app.services.race_management.lap_comparison_service import (
    LapComparisonService,
)

YEAR = 2024
ROUND = 11

PRIMARY_DRIVER = "44"
SECONDARY_DRIVER = "1"


def find_driver(drivers, driver_number):

    for driver in drivers:

        if driver.driver_number == driver_number:
            return driver

    return None


def main():

    race_service = RaceManagementService()

    comparison_service = LapComparisonService()

    drivers = race_service.analyze_race(

        YEAR,
        ROUND,

    )

    ##########################################################
    # Drivers
    ##########################################################

    driver_a = find_driver(
        drivers,
        PRIMARY_DRIVER,
    )

    driver_b = find_driver(
        drivers,
        SECONDARY_DRIVER,
    )

    if driver_a is None or driver_b is None:

        print("Driver not found.")
        return

    ##########################################################

    print()

    print("=" * 80)
    print(
        f"{driver_a.driver_code} vs {driver_b.driver_code}"
    )
    print("=" * 80)

    ##########################################################
    # Compare every stint
    ##########################################################

    for stint_a in driver_a.stints:

        for stint_b in driver_b.stints:

            groups = (

                comparison_service.compare(

                    stint_a,
                    stint_b,

                )

            )

            if not groups:
                continue

            print()

            print(
                f"Stint {stint_a.stint} "
                f"({stint_a.compound})"
                "  vs  "
                f"Stint {stint_b.stint} "
                f"({stint_b.compound})"
            )

            print("-" * 80)

            ##################################################
            # Recommendation Groups
            ##################################################

            for group in groups[:10]:

                print()

                print("=" * 60)

                print(
                    f"{driver_b.driver_code} "
                    f"Lap {group.secondary_lap.lap_number}"
                )

                print("=" * 60)

                for recommendation in group.recommendations:

                    print()

                    print(
                        f"{driver_a.driver_code} "
                        f"Lap {recommendation.lap_a.lap_number}"
                    )

                    print(
                        f"Score : "
                        f"{recommendation.compatibility_score}"
                    )

                    if recommendation.reasons:

                        print()

                        print("Reasons")

                        for reason in recommendation.reasons:

                            print(
                                f"  • {reason}"
                            )

if __name__ == "__main__":
    main()