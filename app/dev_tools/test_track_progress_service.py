from app.services.session_cache_service import get_loaded_session
from app.services.race_management.track_progress_service import (
    TrackProgressService,
)

YEAR = 2024
ROUND = 11
DRIVER = "44"

session = get_loaded_session(
    YEAR,
    ROUND,
)

service = TrackProgressService()

frame = service.build(
    session,
    DRIVER,
)

print()

print("=" * 70)
print("TRACK PROGRESS")
print("=" * 70)

print()

print("Driver:", frame.driver_number)

print("Samples:", len(frame.samples))

print()

print("First 10 Samples")

print("-" * 70)

for sample in frame.samples[:10]:

    print(
        sample.session_time,
        sample.x,
        sample.y,
        sample.status,
    )
    
print()

print("Last 10 Samples")

print("-" * 70)

for sample in frame.samples[-10:]:

    print(
        sample.session_time,
        sample.x,
        sample.y,
        sample.status,
    )
    
xs = [sample.x for sample in frame.samples]
ys = [sample.y for sample in frame.samples]

print()

print("Track Bounds")

print("-" * 70)

print(f"X : {min(xs):.2f} -> {max(xs):.2f}")
print(f"Y : {min(ys):.2f} -> {max(ys):.2f}")