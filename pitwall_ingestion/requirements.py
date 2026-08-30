from __future__ import annotations

# FastF1's native cache resource profiles observed in your PitWall cache.
# Weather and race-control are intentionally excluded from Qualifying for
# Phase 1, per the current PitWall requirement.

QUALIFYING_REQUIRED_FILES = {
    "session_info.ff1pkl",
    "driver_info.ff1pkl",
    "session_status_data.ff1pkl",
    "track_status_data.ff1pkl",
    "_extended_timing_data.ff1pkl",
    "timing_app_data.ff1pkl",
    "car_data.ff1pkl",
    "position_data.ff1pkl",
}

RACE_REQUIRED_FILES = {
    "session_info.ff1pkl",
    "driver_info.ff1pkl",
    "session_status_data.ff1pkl",
    "lap_count.ff1pkl",
    "track_status_data.ff1pkl",
    "_extended_timing_data.ff1pkl",
    "timing_app_data.ff1pkl",
    "car_data.ff1pkl",
    "position_data.ff1pkl",
    "weather_data.ff1pkl",
    "race_control_messages.ff1pkl",
}


def required_files(session_type: str) -> set[str]:
    normalized = session_type.upper()
    if normalized in {"Q", "QUALIFYING"}:
        return QUALIFYING_REQUIRED_FILES
    if normalized in {"R", "RACE"}:
        return RACE_REQUIRED_FILES
    raise ValueError(f"Unsupported session type: {session_type}")
