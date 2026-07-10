from .models import RepresentativeAnalysis, ScoreBreakdown
from .lap_time_consistency_analyzer import LapTimeConsistencyAnalyzer
from .sector_consistency_analyzer import SectorConsistencyAnalyzer
from .position_stability_analyzer import PositionStabilityAnalyzer
from .lap_traffic_analyzer import (
    LapTrafficAnalyzer,
)
from .reason_builder import ReasonBuilder


class RepresentativeLapAnalyzer:
    
    def __init__(
        self,
        lap_traffic_analyzer: LapTrafficAnalyzer,
    ):

        self.lap_time_analyzer = LapTimeConsistencyAnalyzer()
        self.sector_analyzer = SectorConsistencyAnalyzer()
        self.position_analyzer = PositionStabilityAnalyzer()

        self.lap_traffic_analyzer = (
            lap_traffic_analyzer
        )
        self.reason_builder = ReasonBuilder()

    def analyze_stint(
        self,
        stint,
        traffic_frame,
    ):

        for lap in stint.analyzed_laps:

            if not lap.analysis.valid:
                continue

            representative = self._analyze_lap(
                lap,
                stint.analyzed_laps,
                traffic_frame,
            )

            lap.representative = representative
            lap.traffic = representative.traffic

    ###########################################################

    def _analyze_lap(
        self,
        lap,
        stint_laps,
        traffic_frame,
    ):

        ##########################################################
        # Lap Time
        ##########################################################

        lap_time = self.lap_time_analyzer.analyze(
            lap,
            stint_laps
        )

        ##########################################################
        # Sector consistency
        ##########################################################

        sector = self.sector_analyzer.analyze(
            lap,
            stint_laps,
        )
        
        ##########################################################
        # Position consistency
        ##########################################################
        
        position = self.position_analyzer.analyze(
            lap,
            stint_laps,
        )

        ##########################################################
        # Traffic
        ##########################################################

        traffic_samples = (
            traffic_frame.samples_for_lap(
                lap.lap_number
            )
        )

        traffic = (
            self.lap_traffic_analyzer.analyze(
                traffic_samples
            )
        )

        ##########################################################
        # Overall score
        ##########################################################

        overall = round(

            (
                lap_time.score
                + sector.score
                + position.score
                + traffic.traffic_score
            ) / 4

        )

        ##########################################################

        return RepresentativeAnalysis(

            overall_score=overall,

            representative=overall >= 85,

            breakdown=[

                ScoreBreakdown(
                    category="Lap Time",
                    score=lap_time.score,
                    reason=(
                        f"Δ {lap_time.delta_seconds:+.3f}s "
                        f"from median"
                    ),
                ),

                ScoreBreakdown(
                    category="Sector Consistency",
                    score=sector.score,
                    reason=(
                        f"S1 {sector.delta_sector1:+.3f}s | "
                        f"S2 {sector.delta_sector2:+.3f}s | "
                        f"S3 {sector.delta_sector3:+.3f}s"
                    ),
                ),

                ScoreBreakdown(
                    category="Position Stability",
                    score=position.score,
                    reason=(
                        f"Δ {position.delta_position:+.1f} positions"
                    ),
                ),

                ScoreBreakdown(
                    category="Traffic",
                    score=traffic.traffic_score,
                    reason=(
                        "Clean Air"
                        if not traffic.in_dirty_air
                        else "Traffic"
                    ),
                ),
            ],

            reasons=self.reason_builder.build(
                lap,
                lap_time,
                sector,
                position,
                traffic,
            ),
            lap_time=lap_time,
            sector=sector,
            position=position,
            traffic=traffic,
        )