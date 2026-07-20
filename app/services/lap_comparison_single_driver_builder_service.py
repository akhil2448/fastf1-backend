from app.services.race_management.race_management_service import (
    RaceManagementService,
)
from app.services.lap_comparison_single_driver_json_builder import (
    LapComparisonSingleDriverJsonBuilder,
)


class LapComparisonSingleDriverBuilderService:

    def __init__(self):

        self.race_service = (
            RaceManagementService()
        )

        self.json_builder = (
            LapComparisonSingleDriverJsonBuilder()
        )

    ##########################################################

    def build(
        self,
        year,
        round_number,
        driver_code,
    ):

        ######################################################
        # Analyze race
        ######################################################

        drivers = self.race_service.analyze_race(

            year,
            round_number,

        )
        
        ######################################################
        # Driver lookup
        ######################################################

        driver_code_lookup = {

            driver.driver_number: driver.driver_code

            for driver in drivers

        }

        ######################################################
        # Find driver
        ######################################################

        driver = self._find_driver(

            drivers,

            driver_code,

        )

        if driver is None:

            raise ValueError(

                f"Unknown driver: {driver_code}"

            )

       ######################################################
        # Keep only valid laps and sort best first
        ######################################################

        for stint in driver.stints:

            valid_laps = [

                lap

                for lap in stint.analyzed_laps

                if lap.analysis.valid

            ]

            valid_laps.sort(

                key=lambda lap: (

                    lap.representative.overall_score,

                    lap.traffic.traffic_score,

                    -lap.tyre_life,

                ),

                reverse=True,

            )

            ##################################################
            # Replace with sorted list
            ##################################################

            stint.analyzed_laps = valid_laps

        ######################################################

        return self.json_builder.build(

            year=year,

            round_number=round_number,

            driver=driver,

            driver_code_lookup=driver_code_lookup,

        )

    ##########################################################

    def _find_driver(
        self,
        drivers,
        driver_code,
    ):

        driver_code = driver_code.upper()

        for driver in drivers:

            if driver.driver_code == driver_code:

                return driver

        return None