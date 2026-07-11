from app.services.lap_comparison_single_driver_builder_service import (
    LapComparisonSingleDriverBuilderService,
)

YEAR = 2024
ROUND = 11

DRIVER = "HAM"


##############################################################


def print_driver_summary(
    lap,
):

    traffic = lap.traffic

    print(

        f"Lap {lap.lap_number:<2}   "

        f"Pos:{lap.position:<2}   "

        f"{lap.compound:<6}   "

        f"Tyre:{lap.tyre_life:<2}   "

        f"Rep:{lap.representative.overall_score:<3}   "

        f"Traffic:{traffic.traffic_score:<3}   "

        f"Clean:{traffic.clean_air_percentage:>5.1f}%   "

        f"Dirty:{traffic.time_in_dirty_air:>5.1f}%   "

        f"DRS:{traffic.drs_percentage:>5.1f}%   "

        f"DRS→Lead:{traffic.drs_in_dirty_air_percentage:>5.1f}%   "

        f"Wake:{traffic.average_wake_strength * 100:>4.1f}%   "

        f"AvgGap:{'-' if traffic.average_gap_ahead_distance is None else f'{traffic.average_gap_ahead_distance:.1f}m'}   "

        f"Closest:{'-' if traffic.minimum_gap_ahead_distance is None else f'{traffic.minimum_gap_ahead_distance:.1f}m'}   "

        f"Lead:{traffic.nearest_car_ahead or '-'}"

    )


##############################################################


def main():

    builder = (
        LapComparisonSingleDriverBuilderService()
    )

    driver = builder.build(

        year=YEAR,

        round_number=ROUND,

        driver_code=DRIVER,

    )

    print()

    print("=" * 90)

    print(

        f"{driver.driver_code} "

        f"{driver.full_name}"

    )

    print("=" * 90)

    ##########################################################

    for stint in driver.stints:

        print()

        print(

            f"STINT {stint.stint} "

            f"({stint.compound})"

        )

        print("-" * 90)

        print()

        for lap in stint.analyzed_laps:

            if not lap.analysis.valid:
                continue

            print_driver_summary(
                lap
            )

            if lap.representative.reasons:

                for reason in lap.representative.reasons:

                    print(
                        f"   • {reason}"
                    )

            print()


##############################################################


if __name__ == "__main__":

    main()