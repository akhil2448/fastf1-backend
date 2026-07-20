from .models import RaceProgressCollection
from .telemetry_service import TelemetryService
from .race_progress_service import RaceProgressService


class RaceProgressCollectionService:

    """
    Builds RaceProgressFrame objects for every driver in
    the session.

    Traffic analysis and battle detection will use this
    service instead of rebuilding race progress repeatedly.
    """

    def __init__(self):

        self.telemetry_service = TelemetryService()

        self.progress_service = RaceProgressService()

    ##############################################################

    def build(
        self,
        session,
    ) -> RaceProgressCollection:

        collection = RaceProgressCollection()

        ##########################################################
        # Build every driver's progress
        ##########################################################

        for driver_number in session.drivers:

            telemetry = self.telemetry_service.build(
                session,
                driver_number,
            )

            progress = self.progress_service.build(
                telemetry,
            )

            collection.drivers[
                driver_number
            ] = progress

        ##########################################################

        return collection