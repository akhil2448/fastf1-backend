from app.services.race_management.race_management_service import RaceManagementService

YEAR = 2024
ROUND = 11
DRIVER = "HAM"

service = RaceManagementService()

drivers = service.analyze_race(YEAR, ROUND)

driver = next(
    d for d in drivers
    if d.driver_code == DRIVER
)

for stint in driver.stints:

    print("=" * 70)
    print(f"STINT {stint.stint}")
    print("=" * 70)

    for lap in stint.analyzed_laps:

        if not lap.analysis.valid:
            continue

        lt = lap.representative.lap_time
        sector = lap.representative.sector
        position = lap.representative.position

        print("=" * 60)

        print(f"Lap {lap.lap_number}")

        print(
            f"Overall Score : "
            f"{lap.representative.overall_score}"
        )

        print()

        print(
            f"Expected Lap : "
            f"{lt.expected_lap_time:.3f}"
        )

        print(
            f"Actual Lap   : "
            f"{lt.actual_lap_time:.3f}"
        )

        print(
            f"Delta        : "
            f"{lt.delta_seconds:+.3f}"
        )
        
        ##########################################################
        # Position details
        ##########################################################

        print(
            f"Expected Position : "
            f"{position.expected_position:.1f}"
        )

        print(
            f"Actual Position   : "
            f"{position.actual_position}"
        )

        print(
            f"Position Delta    : "
            f"{position.delta_position:+.1f}"
        )

        print()

        ##########################################################
        # Sector details
        ##########################################################

        print(
            f"Sector Deltas     : "
            f"S1 {sector.delta_sector1:+.3f}   "
            f"S2 {sector.delta_sector2:+.3f}   "
            f"S3 {sector.delta_sector3:+.3f}"
        )

        print()

        for item in lap.representative.breakdown:

            print(
                f"{item.category:<22}"
                f"{item.score:>3}"
                f"   {item.reason}"
            )

        print()