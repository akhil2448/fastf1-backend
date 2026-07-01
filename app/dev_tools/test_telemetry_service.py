from app.services.session_cache_service import get_loaded_session
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

service = TelemetryService()

frame = service.build(
    session,
    DRIVER,
)

print()

print("=" * 70)
print("TELEMETRY")
print("=" * 70)

print()

print("Driver :", frame.driver_number)

print("Samples:", len(frame.samples))

print()

print("First 10 Samples")

print("-" * 70)

for sample in frame.samples[:10]:

    print(

        sample.lap_number,

        f"{sample.distance:.1f}",

        f"{sample.normalized_distance:.3f}",

        sample.speed,

        sample.throttle,

        sample.brake,
    )