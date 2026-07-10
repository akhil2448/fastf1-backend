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

def print_driver_summary(
    driver_code,
    lap,
):

    traffic = lap.traffic

    print(

        f"{driver_code:<3} "

        f"Lap {lap.lap_number:<2}   "

        f"{lap.compound:<6}   "

        f"Tyre:{lap.tyre_life:<2}   "

        f"Rep:{lap.representative.overall_score:<3}   "

        f"Traffic:{traffic.traffic_score:<3}   "

        f"Clean:{traffic.clean_air_percentage:>5.1f}%   "

        f"Dirty:{traffic.time_in_dirty_air:>5.1f}%   "
        
        f"DRS:{traffic.drs_percentage:>5.1f}%   "

        f"DRS→Lead:{traffic.drs_in_dirty_air_percentage:>5.1f}%   "

        f"Wake:{traffic.average_wake_strength * 100:>4.1f}%(avg)/"
        f"{traffic.maximum_wake_strength * 100:>4.1f}%(max)   "

        f"Avg Gap:{'-' if traffic.average_gap_ahead_distance is None else f'{traffic.average_gap_ahead_distance:.1f}m'}   "

        f"Closest Gap:{'-' if traffic.minimum_gap_ahead_distance is None else f'{traffic.minimum_gap_ahead_distance:.1f}m'}   "

        f"Lead:{traffic.nearest_car_ahead or '-'}"

    )

##############################################################


def print_traffic(
    driver_code,
    traffic,
):

    print()

    print(driver_code)

    print("-" * 30)

    print(
        f"Traffic Score        : "
        f"{traffic.traffic_score}"
    )

    print(
        f"Clean Air            : "
        f"{traffic.clean_air_percentage:.1f}%"
    )

    print(
        f"Time In Dirty Air    : "
        f"{traffic.time_in_dirty_air:.1f}%"
    )
    
    print(
        f"DRS Usage            : "
        f"{traffic.drs_percentage:.1f}%"
    )

    print(
        f"DRS While Following  : "
        f"{traffic.drs_in_dirty_air_percentage:.1f}%"
    )

    print(
        f"Weighted Dirty Air   : "
        f"{traffic.dirty_air_percentage:.1f}%"
    )

    print(
        f"Average Wake         : "
        f"{traffic.average_wake_strength:.3f}"
    )

    print(
        f"Maximum Wake         : "
        f"{traffic.maximum_wake_strength:.3f}"
    )

    print(
        f"Average Gap Ahead    : "
        f"{traffic.average_gap_ahead_distance}"
    )

    print(
        f"Closest Gap Ahead    : "
        f"{traffic.minimum_gap_ahead_distance}"
    )

    print(
        f"Representative Car   : "
        f"{traffic.nearest_car_ahead}"
    )

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
                        f"Compatibility Score : "
                        f"{recommendation.compatibility_score}"
                    )

                    print()

                    print_driver_summary(

                        driver_a.driver_code,

                        recommendation.lap_a,

                    )

                    print()

                    print_driver_summary(

                        driver_b.driver_code,

                        recommendation.lap_b,

                    )
                    
                    print()

                    if recommendation.reasons:

                        print("Reasons")
                        print("-" * 40)

                        for reason in recommendation.reasons:

                            print(f"• {reason}")

if __name__ == "__main__":
    main()