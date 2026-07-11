from app.services.session_cache_service import (
    get_loaded_session,
)

from app.services.race_management_drivers_json_builder import (
    RaceManagementDriversJsonBuilder,
)


class RaceManagementDriversBuilderService:

    def __init__(self):

        self.json_builder = (
            RaceManagementDriversJsonBuilder()
        )

    ##########################################################

    def build(
        self,
        year,
        round_number,
    ):

        ######################################################
        # Load session
        ######################################################

        session = get_loaded_session(

            year,
            round_number,

        )

        ######################################################
        # JSON
        ######################################################

        return self.json_builder.build(

            year=year,

            round_number=round_number,

            session=session,

        )