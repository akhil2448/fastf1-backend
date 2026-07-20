from app.services.session_cache_service import get_loaded_session

from .stint_analyzer import StintAnalyzer
from .models import DriverRaceAnalysis
from .representative_lap_analyzer import RepresentativeLapAnalyzer
from .race_timeline_service import RaceTimelineService

from .race_progress_collection_service import (RaceProgressCollectionService,)

from .traffic_index_builder import (TrafficIndexBuilder,)

from .track_length_service import (TrackLengthService,)

from .wake_profile_service import WakeProfileService
from .wake_model import WakeModel
from .traffic_analyzer import TrafficAnalyzer
from .lap_traffic_analyzer import LapTrafficAnalyzer


class RaceManagementService:

    def __init__(self):

        self.stint_analyzer = StintAnalyzer()
        self.timeline_service = (
            RaceTimelineService()
        )

        self.progress_collection_service = (
            RaceProgressCollectionService()
        )

        self.traffic_index_builder = (
            TrafficIndexBuilder()
        )
        
        self.track_length_service = (
            TrackLengthService()
        )

    def analyze_race(
        self,
        year: int,
        round_number: int,
    ):

        session = get_loaded_session(
            year,
            round_number,
        )
        
        profile = (
            WakeProfileService()
            .get_profile(year)
        )

        wake_model = WakeModel(
            profile
        )

        traffic_analyzer = TrafficAnalyzer(
            wake_model
        )

        lap_traffic_analyzer = LapTrafficAnalyzer(
            traffic_analyzer
        )

        representative_lap_analyzer = (
            RepresentativeLapAnalyzer(
                lap_traffic_analyzer
            )
        )
        
        ##########################################################
        # Build race-wide data once
        ##########################################################

        timeline = self.timeline_service.build(
            session
        )

        progress_collection = (
            self.progress_collection_service.build(
                session
            )
        )
        
        track_length = (
            self.track_length_service.get_track_length(
                session
            )
        )

        drivers = []

        for driver_number in session.drivers:

            driver_info = session.get_driver(driver_number)

            driver_laps = session.laps.pick_drivers(
                driver_number
            )

            stints = self.stint_analyzer.analyze(

                driver_laps,

                driver_number,

                driver_info["Abbreviation"],

            )
            
            valid_laps = sum(
                lap.analysis.valid
                for stint in stints
                for lap in stint.analyzed_laps
            )

            # Skip drivers that have no usable race laps
            if valid_laps == 0:
                continue
            
            traffic_frame = (
                self.traffic_index_builder.build(
                    timeline,
                    progress_collection,
                    track_length,
                    driver_number,
                )
            )
            
            for stint in stints:

                representative_lap_analyzer.analyze_stint(
                    stint,
                    traffic_frame,
                )

            drivers.append(
                DriverRaceAnalysis(
                    driver_number=driver_number,
                    driver_code=driver_info["Abbreviation"],
                    full_name=driver_info["FullName"],
                    team_name=driver_info["TeamName"],
                    team_color=driver_info["TeamColor"],
                    stints=stints,
                )
            )

        return drivers