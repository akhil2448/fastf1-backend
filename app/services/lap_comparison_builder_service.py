from app.services.race_management.race_management_service import (
    RaceManagementService,
)

from app.services.race_management.lap_comparison_service import (
    LapComparisonService,
)

from app.services.race_management.stint_comparison_result import (
    StintComparisonResult,
)

from app.services.lap_comparison_json_builder import (
    LapComparisonJsonBuilder,
)


class LapComparisonBuilderService:

    def __init__(self):

        self.race_service = (
            RaceManagementService()
        )

        self.comparison_service = (
            LapComparisonService()
        )

        self.json_builder = (
            LapComparisonJsonBuilder()
        )

    ##########################################################

    def build(
        self,
        year,
        round_number,
        primary_driver,
        secondary_driver,
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
        # Find drivers
        ######################################################

        driver_a = self._find_driver(

            drivers,
            primary_driver,

        )

        driver_b = self._find_driver(

            drivers,
            secondary_driver,

        )

        if driver_a is None:

            raise ValueError(
                f"Unknown driver: {primary_driver}"
            )

        if driver_b is None:

            raise ValueError(
                f"Unknown driver: {secondary_driver}"
            )

        ######################################################
        # Compare stints
        ######################################################

        stint_comparisons = []

        for stint_a in driver_a.stints:

            for stint_b in driver_b.stints:

                groups = (

                    self.comparison_service.compare(

                        stint_a,

                        stint_b,

                    )

                )

                if not groups:
                    continue

                stint_comparisons.append(

                    StintComparisonResult(

                        driver_a_stint=(
                            stint_a.stint
                        ),

                        driver_b_stint=(
                            stint_b.stint
                        ),

                        compound_a=(
                            stint_a.compound
                        ),

                        compound_b=(
                            stint_b.compound
                        ),

                        groups=groups,

                    )

                )

        ######################################################
        # JSON
        ######################################################

        return self.json_builder.build(

            year=year,

            round_number=round_number,

            driver_a=driver_a,

            driver_b=driver_b,

            stint_comparisons=(
                stint_comparisons
            ),

            driver_code_lookup=(
                driver_code_lookup
            ),

        )

    ##########################################################

    def _find_driver(
        self,
        drivers,
        driver_code,
    ):

        driver_code = driver_code.upper()

        for driver in drivers:

            if (
                driver.driver_code
                == driver_code
            ):

                return driver

        return None