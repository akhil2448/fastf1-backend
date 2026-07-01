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

    print()
    print("=" * 120)
    print(f"Race Management Analysis ({YEAR} Round {ROUND})")
    print("=" * 120)

    print(f"\nDrivers available: {len(drivers)}\n")

    for driver in drivers:

        print("-" * 120)
        print(f"{driver.driver_code} - {driver.full_name}")
        print(f"Team : {driver.team_name}")

        total_valid = 0

        for stint in driver.stints:

            valid_laps = sum(
                lap.analysis.valid
                for lap in stint.analyzed_laps
            )

            total_valid += valid_laps

            print(
                f"\n"
                f"Stint {stint.stint} | "
                f"{stint.compound:<8} | "
                f"Laps {stint.start_lap:>2}-{stint.end_lap:<2} | "
                f"Tyre Age {stint.tyre_life_start:>2}-{stint.tyre_life_end:<2} | "
                f"Valid {valid_laps:>2}/{stint.total_laps}"
            )

            valid_laps = [
                lap
                for lap in stint.analyzed_laps
                if lap.analysis.valid
            ]

            print(
                "Valid Laps :",
                [lap.lap_number for lap in valid_laps],
            )

            if valid_laps:

                representative = valid_laps[0].representative

                print(
                    "Traffic Score :",
                    representative.traffic.traffic_score,
                )

                print(
                    "Dirty Air %   :",
                    f"{representative.traffic.dirty_air_percentage:.1f}",
                )

                print(
                    "Nearest Ahead :",
                    representative.traffic.nearest_car_ahead,
                )

        print(f"\nTotal Valid Laps : {total_valid}")
        print()

    print("=" * 120)


if __name__ == "__main__":
    main()