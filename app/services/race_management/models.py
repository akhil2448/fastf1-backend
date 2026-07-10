from dataclasses import dataclass, field
from datetime import timedelta


@dataclass
class LapAnalysisResult:
    """
    Result of analysing a single race lap.
    """

    valid: bool
    reasons: list[str] = field(default_factory=list)


@dataclass
class AnalyzedLap:
    """
    Canonical representation of one race lap.

    Every future analyzer enriches this object instead of
    repeatedly reading FastF1 data.
    """

    ###########################################################
    # Identity
    ###########################################################

    driver_number: str
    driver_code: str
    
    lap_number: int
    stint: int

    ###########################################################
    # Tyres
    ###########################################################

    compound: str
    normalized_compound: str
    tyre_life: int
    fresh_tyre: bool

    ###########################################################
    # Timing
    ###########################################################

    lap_time: timedelta
    lap_start_time: timedelta
    lap_end_time: timedelta
    sector1_time: timedelta
    sector2_time: timedelta
    sector3_time: timedelta

    ###########################################################
    # Race state
    ###########################################################

    position: int
    track_status: str
    deleted: bool

    ###########################################################
    # Speed traps
    ###########################################################

    speed_i1: float
    speed_i2: float
    speed_fl: float
    speed_st: float

    ###########################################################
    # Analysis (filled later)
    ###########################################################

    analysis: LapAnalysisResult
    traffic: TrafficAnalysis | None = None
    representative: RepresentativeAnalysis | None = None
    


@dataclass
class StintAnalysisResult:

    stint: int
    compound: str
    tyre_life_start: int
    tyre_life_end: int
    start_lap: int
    end_lap: int
    total_laps: int
    analyzed_laps: list[AnalyzedLap] = field(default_factory=list)
    

@dataclass
class DriverRaceAnalysis:

    driver_number: str
    driver_code: str
    full_name: str
    team_name: str
    team_color: str
    stints: list[StintAnalysisResult] = field(default_factory=list)
    

@dataclass
class ScoreBreakdown:

    category: str
    score: int
    reason: str
    
@dataclass
class LapTimeConsistency:

    expected_lap_time: float
    actual_lap_time: float
    delta_seconds: float
    median_window_size: int
    score: int
    representative: bool
    reasons: list[str] = field(default_factory=list)
    

@dataclass
class RepresentativeAnalysis:

    overall_score: int
    representative: bool
    breakdown: list[ScoreBreakdown] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    lap_time: LapTimeConsistency | None = None
    sector: SectorConsistency | None = None
    position: PositionStability | None = None
    traffic: TrafficAnalysis | None = None
    

@dataclass
class SectorConsistency:

    expected_sector1: float
    actual_sector1: float
    delta_sector1: float

    expected_sector2: float
    actual_sector2: float
    delta_sector2: float

    expected_sector3: float
    actual_sector3: float
    delta_sector3: float

    score: int

    representative: bool
    reasons: list[str] = field(default_factory=list)
    
    
@dataclass
class PositionStability:

    expected_position: float
    actual_position: int
    delta_position: float
    score: int
    representative: bool
    reasons: list[str] = field(default_factory=list)

@dataclass
class TrafficAnalysis:

    nearest_car_ahead: str | None
    gap_ahead_progress: float | None
    nearest_car_behind: str | None
    gap_behind_progress: float | None
    gap_ahead_distance: float | None
    gap_behind_distance: float | None
    in_dirty_air: bool
    dirty_air_percentage: float
    minimum_gap_ahead_progress: float | None
    traffic_score: int
    ##########################################################
    # Lap summary
    ##########################################################

    clean_air_percentage: float
    average_wake_strength: float
    maximum_wake_strength: float
    time_in_dirty_air: float
    average_gap_ahead_distance: float | None
    minimum_gap_ahead_distance: float | None
    representative: bool

    wake: WakeAnalysis | None
    reasons: list[str] = field(default_factory=list)

@dataclass
class TrackProgressSample:
    """
    Canonical representation of one position sample.
    Progress will be calculated later.
    """

    session_time: timedelta
    x: float
    y: float
    status: str


@dataclass
class TrackProgressFrame:
    """
    All position samples for one driver.
    """

    driver_number: str
    samples: list[TrackProgressSample] = field(default_factory=list)
    
@dataclass
class RaceProgressSample:
    """
    Canonical representation of one telemetry sample.
    """

    session_time: timedelta
    lap_number: int
    distance: float
    normalized_progress: float
    speed: float
    drs: int


@dataclass
class RaceProgressFrame:
    """
    All telemetry progress samples for one driver.
    """

    driver_number: str
    samples: list[RaceProgressSample] = field(default_factory=list)
    
@dataclass
class TelemetrySample:
    """
    Canonical representation of one telemetry sample.
    """

    session_time: timedelta
    lap_number: int
    distance: float
    normalized_distance: float
    speed: float
    rpm: float
    throttle: float
    brake: bool
    gear: int
    drs: int


@dataclass
class TelemetryFrame:
    """
    Canonical telemetry for one driver across the entire race.
    """

    driver_number: str
    samples: list[TelemetrySample] = field(default_factory=list)
    

@dataclass
class RaceProgressCollection:
    """
    Race progress for every driver in the session.
    """

    drivers: dict[str, RaceProgressFrame] = field(
        default_factory=dict
    )
    
@dataclass
class TrafficNeighbour:
    """
    One nearby car.
    """

    driver_number: str
    gap_progress: float
    gap_distance: float


@dataclass
class TrafficSample:
    """
    Traffic situation for one telemetry sample.
    """

    session_time: timedelta
    lap_number: int
    normalized_progress: float
    speed: float
    drs: int
    nearest_ahead: TrafficNeighbour | None = None
    nearest_behind: TrafficNeighbour | None = None


@dataclass
class TrafficFrame:
    """
    Traffic information for one driver.
    """

    driver_number: str
    samples: list[TrafficSample] = field(default_factory=list)
    
    def samples_for_lap(
        self,
        lap_number: int,
    ):

        return [
            sample
            for sample in self.samples
            if sample.lap_number == lap_number
        ]
    

@dataclass
class DriverLapTimeline:
    """
    Timing information for one completed lap.
    """

    lap_number: int
    lap_start_time: timedelta
    lap_end_time: timedelta
    lap_time: timedelta
    cumulative_time: timedelta


@dataclass
class DriverTimeline:
    """
    Timeline for one driver.
    """

    driver_number: str
    laps: list[DriverLapTimeline] = field(default_factory=list)
    laps_by_number: dict[int, DriverLapTimeline] = field(
        default_factory=dict
    )


@dataclass
class RaceTimeline:
    """
    Timeline for the whole race.
    """
    
    drivers: dict[str, DriverTimeline] = field(default_factory=dict)
    

@dataclass
class WakeResult:

    strength: float
    in_dirty_air: bool
    
    
@dataclass
class WakeAnalysis:

    profile: str
    distance_weight: float
    speed_factor: float
    drs_factor: float
    final_weight: float
    in_dirty_air: bool
    gap_distance: float | None