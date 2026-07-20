from app.services.race_management.race_management_service import (
    RaceManagementService,
)

YEAR = 2024
ROUND = 11


def main():

    service = RaceManagementService()

    drivers = service.analyze_race(
        YEAR,
        ROUND,
    )

    ##############################################################
    # Header
    ##############################################################

    print()

    print("=" * 110)
    print("DIRTY AIR DISTRIBUTION")
    print("=" * 110)

    print()

    print(
        f"{'Driver':<8}"
        f"{'Lap':>5}"
        f"{'Dirty %':>10}"
        f"{'Score':>8}"
        f"{'Ahead':>8}"
        f"{'Rep':>8}"
    )

    print("-" * 110)

    ##############################################################
    # Statistics
    ##############################################################

    dirty_percentages = []

    bucket_0_5 = 0
    bucket_5_10 = 0
    bucket_10_20 = 0
    bucket_20_30 = 0
    bucket_30_40 = 0
    bucket_40_50 = 0
    bucket_50_60 = 0
    bucket_60_plus = 0

    ##############################################################

    for driver in drivers:

        for stint in driver.stints:

            for lap in stint.analyzed_laps:

                if not lap.analysis.valid:
                    continue

                traffic = lap.representative.traffic

                dirty = traffic.dirty_air_percentage

                dirty_percentages.append(
                    dirty
                )

                ##################################################
                # Histogram
                ##################################################

                if dirty < 5:
                    bucket_0_5 += 1

                elif dirty < 10:
                    bucket_5_10 += 1

                elif dirty < 20:
                    bucket_10_20 += 1

                elif dirty < 30:
                    bucket_20_30 += 1

                elif dirty < 40:
                    bucket_30_40 += 1

                elif dirty < 50:
                    bucket_40_50 += 1

                elif dirty < 60:
                    bucket_50_60 += 1

                else:
                    bucket_60_plus += 1

                ##################################################

                print(

                    f"{driver.driver_code:<8}"

                    f"{lap.lap_number:>5}"

                    f"{dirty:>10.1f}"

                    f"{traffic.traffic_score:>8}"

                    f"{str(traffic.nearest_car_ahead):>8}"

                    f"{str(traffic.representative):>8}"

                )

    ##############################################################
    # Summary
    ##############################################################

    print()

    print("=" * 110)
    print("SUMMARY")
    print("=" * 110)

    print()

    print(
        f"Total Valid Laps : {len(dirty_percentages)}"
    )

    print(
        f"Minimum Dirty % : {min(dirty_percentages):.1f}"
    )

    print(
        f"Maximum Dirty % : {max(dirty_percentages):.1f}"
    )

    print(
        "Average Dirty % : "
        f"{sum(dirty_percentages) / len(dirty_percentages):.1f}"
    )

    print()

    print("Histogram")
    print("-" * 40)

    print(f"  0 -  5% : {bucket_0_5}")
    print(f"  5 - 10% : {bucket_5_10}")
    print(f" 10 - 20% : {bucket_10_20}")
    print(f" 20 - 30% : {bucket_20_30}")
    print(f" 30 - 40% : {bucket_30_40}")
    print(f" 40 - 50% : {bucket_40_50}")
    print(f" 50 - 60% : {bucket_50_60}")
    print(f" 60%+     : {bucket_60_plus}")

    print()

    print("=" * 110)


if __name__ == "__main__":
    main()