from app.services.session_cache_service import get_loaded_session
from app.services.race_management.race_progress_service import (
    RaceProgressService,
)
from app.services.race_management.telemetry_service import (
    TelemetryService,
)

YEAR = 2024
ROUND = 11
DRIVER = "44"

session = get_loaded_session(
    YEAR,
    ROUND,
)

telemetry_service = TelemetryService()

telemetry = telemetry_service.build(
    session,
    DRIVER,
)

service = RaceProgressService()

frame = service.build(
    telemetry,
)

print()

print("Driver:", frame.driver_number)

print("Samples:", len(frame.samples))

print()

print("First 10")

print("-" * 70)

for sample in frame.samples[:10]:

    print(
        sample.session_time,
        sample.lap_number,
        f"{sample.distance:.1f}",
        f"{sample.normalized_progress:.3f}",
        f"{sample.speed:.1f}",
    )

print()

print("Last 10")

print("-" * 70)

for sample in frame.samples[-10:]:

    print(
        sample.session_time,
        sample.lap_number,
        f"{sample.distance:.1f}",
        f"{sample.normalized_progress:.3f}",
        f"{sample.speed:.1f}",
    )