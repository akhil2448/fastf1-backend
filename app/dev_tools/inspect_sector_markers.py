from app.services.session_cache_service import get_loaded_qualifying_session

YEAR = 2024
ROUND = 11
DRIVER = "VER"

session = get_loaded_qualifying_session(YEAR, ROUND)

lap = (
    session.laps
    .pick_drivers(DRIVER)
    .pick_fastest()
)

telemetry = lap.get_telemetry()

sector1 = lap["Sector1Time"].total_seconds()

print(f"Sector 1 Time: {sector1:.3f}\n")

mask = (
    (telemetry["Time"].dt.total_seconds() >= sector1 - 0.3)
    &
    (telemetry["Time"].dt.total_seconds() <= sector1 + 0.3)
)

print(
    telemetry.loc[
        mask,
        ["Time", "Distance", "RelativeDistance", "Speed"]
    ]
)

