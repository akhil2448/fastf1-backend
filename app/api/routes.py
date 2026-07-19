from fastapi import APIRouter, HTTPException
import fastf1
import traceback
#from typing import Optional

from app.services.qualifying_results import generate_qualifying_results
from app.services.session_cache_service import get_loaded_session
#from app.services.session_data_service import load_race_laps_and_weather
from app.services.race_service import (
    generate_race_json,
    build_red_flag_metadata,
    inject_race_distance_reduction_message,
)
from app.services.circuit_service import generate_track_map
from app.services.year_schedule_service import generate_year_schedule
from app.services.weather_service import build_weather_json
from app.services.track_status_service import build_track_status_json
from app.utils.time_utils import convert_all_timedelta_columns
from app.utils.json_utils import sanitize_for_json
from app.services.telemetry_animation_chunk_writer import generate_race_telemetry
from app.services.driver_telemetry_service import get_driver_telemetry
from app.services.race_classification_service import ( RaceClassificationService )
from app.services.race_control_service import build_race_control_json
from app.services.qualifying_comparison_service import (QualifyingComparisonService)
from app.services.qualifying_drivers_selection import (generate_driver_selection)
from app.services.lap_comparison_builder_service import (LapComparisonBuilderService,)
from app.services.lap_comparison_single_driver_builder_service import (LapComparisonSingleDriverBuilderService,)
from app.services.race_management_drivers_builder_service import (RaceManagementDriversBuilderService,)
from app.services.starting_grid_service import (StartingGridService,)


router = APIRouter(prefix="/api")

# telemetry_cache[(year, round)] = telemetry_json
telemetry_cache = {}

classification_service = RaceClassificationService()
qualifying_comparison_service = (
    QualifyingComparisonService()
)

lap_comparison_builder = (
    LapComparisonBuilderService()
)

single_driver_lap_builder = (
    LapComparisonSingleDriverBuilderService()
)

race_management_drivers_builder = (
    RaceManagementDriversBuilderService()
)

starting_grid_service = (
    StartingGridService()
)

# -------------------- YEAR SCHEDULE --------------------
@router.get("/schedule/{year}")
def get_year_schedule(year: int):
    """
    Returns the full F1 event schedule for a given year.
    """
    return generate_year_schedule(year)


# -------------------- QUALIFYING RESULTS --------------------
@router.get("/qualifying/{year}/{round}")
def get_qualifying_results(
    year: int,
    round: int
):
    """
    Returns:
    - Qualifying results (Q1/Q2/Q3)
    - Final qualifying session reached
    - Final qualifying lap time
    - Race starting grid positions
    """

    try:

        qualifying_results = generate_qualifying_results(
            year=year,
            round_number=round
        )

        return sanitize_for_json(
            qualifying_results
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to build qualifying results: "
                f"{str(e)}"
            )
        )

# -------------------- STARTING GRID --------------------
@router.get("/starting-grid/{year}/{round}")
def get_starting_grid(
    year: int,
    round: int,
):
    """
    Returns the official starting grid together with
    each driver's starting tyre compound.
    """

    try:

        return sanitize_for_json(
            starting_grid_service.get_starting_grid(
                year=year,
                round_number=round,
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to build starting grid: "
                f"{str(e)}"
            )
        )

# -------------------- RACE DATA --------------------
@router.get("/race/{year}/{round}")
def get_race(year: int, round: int):
    
    session = get_loaded_session(year, round)

    laps_df = session.laps
    track_status_df = session.track_status.copy()
    calendar_date = session.event["EventDate"].date()

    classification_data = (
        classification_service.build_classification(
            year=year,
            round_number=round
        )
    )

    race_json = generate_race_json(
        laps=laps_df,
        session=session,
        calendar_date=calendar_date,
        classification_data=classification_data,
        track_status_df=track_status_df
    )

    return sanitize_for_json(race_json)


# -------------------- WEATHER DATA --------------------
@router.get("/weather/{year}/{round}")
def get_weather(year: int, round: int):
    session = get_loaded_session(year, round)

    weather_df = convert_all_timedelta_columns(session.weather_data)
    calendar_date = session.event["EventDate"].date()

    return build_weather_json(weather_df, session, calendar_date)

# -------------------- RACE CONTROL --------------------
@router.get("/race-control/{year}/{round}")
def get_race_control(year: int, round: int):

    session = get_loaded_session(year, round)

    calendar_date = session.event["EventDate"].date()

    classification_data = (
        classification_service.build_classification(
            year=year,
            round_number=round
        )
    )

    race_start_time = (
        session.laps
        .loc[
            session.laps["LapNumber"] == 1,
            "LapStartTime"
        ]
        .min()
    )

    red_flag_metadata = build_red_flag_metadata(
        session.laps,
        session.track_status.copy(),
        race_start_time
    )

    synthetic_messages = (
        inject_race_distance_reduction_message(
            red_flag_metadata,
            session.total_laps,
            classification_data["totalLaps"]
        )
    )

    return build_race_control_json(
        session=session,
        calendar_date=calendar_date,
        synthetic_messages=synthetic_messages
    )

# -------------------- TRACK STATUS --------------------
@router.get("/track-status/{year}/{round}")
def get_track_status(year: int, round: int):
    session = get_loaded_session(year, round)

    calendar_date = session.event["EventDate"].date()

    # IMPORTANT:
    # session.track_status is the correct source
    track_status_df = session.track_status.copy()

    return build_track_status_json(
        track_status_df=track_status_df,
        session=session,
        calendar_date=calendar_date
    )

# -------------------- RACE CLASSIFICATION --------------------
# @router.get("/race-results/{year}/{round}")
# def get_race_results(year: int, round: int):

#     try:
#         classification = classification_service.build_classification(
#             year=year,
#             round_number=round
#         )

#         return sanitize_for_json(classification)

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to build race classification: {str(e)}"
#         )


# -------------------- TRACK MAP --------------------
@router.get("/track-map/{year}/{round}")
def get_track_map(year: int, round: int):
    session = get_loaded_session(year, round)
    return generate_track_map(session)



# -------------------- RACE TELEMETRY --------------------
@router.get("/telemetry/{year}/{round}")
def get_race_telemetry(
    year: int,
    round: int,
    from_second: int,
    to_second: int
):
    """
    Returns telemetry animation snapshots for a race
    between [from_second, to_second].

    Example:
    /telemetry/2021/7?from_second=1832&to_second=2432
    """

    MAX_WINDOW = 600  # seconds (10 minutes)

    # --- Validation ---
    if to_second < from_second:
        raise HTTPException(
            status_code=400,
            detail="to_second must be greater than or equal to from_second"
        )

    if (to_second - from_second) > MAX_WINDOW:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum telemetry window is {MAX_WINDOW} seconds (10 minutes)"
        )

    cache_key = (year, round)

    # --- Load & cache telemetry once per race ---
    if cache_key not in telemetry_cache:
        session = get_loaded_session(year, round)

        telemetry_cache[cache_key] = generate_race_telemetry(session)

    telemetry_data = telemetry_cache[cache_key]

    all_frames = telemetry_data["frames"]
    all_timing_events = telemetry_data["timingEvents"]

    # --- Slice requested animation frames ---
    frames = {
        sec: all_frames[sec]
        for sec in range(from_second, to_second + 1)
        if sec in all_frames
    }
    
    # --- Slice timing events ---
    timing_events = [
        event
        for event in all_timing_events
        if from_second <= event["raceTime"] <= to_second
    ]

    return {
        "from": from_second,
        "to": to_second,
        "frames": frames,
        "timingEvents": timing_events
    }


# -------------------- DRIVER TELEMETRY --------------------
@router.get("/driver-telemetry/{year}/{round}/{driver}")
def get_driver_telemetry_route(
    year: int,
    round: int,
    driver: str,
    from_second: float,
    to_second: float,
    sample_rate_ms: int = 100
):
    """
    Returns high-resolution telemetry for a specific driver
    between race-relative time window.

    Example:
    /driver-telemetry/2021/7/LEC?from_second=1832&to_second=2432&sample_rate_ms=100
    """

    MAX_WINDOW = 600  # seconds (10 minutes)

    # --- Validation ---
    if to_second < from_second:
        raise HTTPException(
            status_code=400,
            detail="to_second must be greater than or equal to from_second"
        )

    if (to_second - from_second) > MAX_WINDOW:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum driver telemetry window is {MAX_WINDOW} seconds"
        )

    if sample_rate_ms < 50:
        raise HTTPException(
            status_code=400,
            detail="sample_rate_ms must be >= 50 ms"
        )

    # --- Load session ---
    session = get_loaded_session(year, round)

    telemetry = get_driver_telemetry(
        session=session,
        driver_code=driver.upper(),
        from_race_second=from_second,
        to_race_second=to_second,
        sample_rate_ms=sample_rate_ms
    )

    return {
        "driver": driver.upper(),
        "from": from_second,
        "to": to_second,
        "sampleRateMs": sample_rate_ms,
        "count": len(telemetry),
        "telemetry": telemetry
    }
    
# -------------------- ULTIMATE PACE --------------------
@router.get("/ultimate-pace/{year}/{round}")
def get_driver_selection(
    year: int,
    round: int
):
    """
    Returns the available drivers for Q1, Q2 and Q3.
    """

    try:

        response = generate_driver_selection(
            year=year,
            round_number=round
        )

        return sanitize_for_json(
            response
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to build driver selection: "
                f"{str(e)}"
            )
        )
        
# -------------------- RACE MANAGEMENT DRIVERS --------------------

@router.get(
    "/race-management/{year}/{round}/drivers"
)
def get_race_management_drivers(
    year: int,
    round: int,
):

    """
    Example

    /api/race-management/2024/11/drivers
    """

    try:

        return race_management_drivers_builder.build(

            year=year,

            round_number=round,

        )

    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to build race management drivers: {str(e)}",
        )
    
@router.get(
    "/qualifying-comparison/{year}/{round}/{session_part}"
)
def get_qualifying_comparison(
    year: int,
    round: int,
    session_part: str,
    driverA: str,
    driverB: str | None = None
):
    """
    Example:

    /api/qualifying-comparison/2021/8/Q3
        ?driverA=VER
        &driverB=HAM
    """
    
    if session_part.upper() not in ["Q1", "Q2", "Q3"]:
        raise HTTPException(
            status_code=400,
            detail="session_part must be Q1, Q2 or Q3"
        )

    return qualifying_comparison_service.build_comparison_payload(
        year=year,
        round_number=round,
        session_part=session_part.upper(),
        driver_a=driverA,
        driver_b=driverB
    )
    

# -------------------- RACE LAP COMPARISON --------------------

@router.get("/race-management/{year}/{round}")
def get_lap_comparison(
    year: int,
    round: int,
    driverA: str,
    driverB: str,
):

    """
    Example

    /api/race-management/2024/11
        ?driverA=HAM
        &driverB=VER
    """

    try:

        return lap_comparison_builder.build(

            year=year,

            round_number=round,

            primary_driver=driverA,

            secondary_driver=driverB,

        )

    except Exception as e:
        
        traceback.print_exc()

        raise HTTPException(

            status_code=500,

            detail=(
                f"Failed to build lap comparison: "
                f"{str(e)}"
            ),

        )
        

# -------------------- SINGLE DRIVER LAP ANALYSIS --------------------

@router.get("/race-management/{year}/{round}/{driver}")
def get_single_driver_laps(
    year: int,
    round: int,
    driver: str,
):

    """
    Example

    /api/race-management/2024/11/HAM
    """

    try:

        return single_driver_lap_builder.build(

            year=year,

            round_number=round,

            driver_code=driver,

        )

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(

                f"Failed to build single driver lap analysis: "

                f"{str(e)}"

            ),

        )