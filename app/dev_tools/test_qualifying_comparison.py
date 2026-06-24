from app.services.qualifying_comparison_service import (
    QualifyingComparisonService
)

service = QualifyingComparisonService()

result = service.build_lap_telemetry(
    year=2021,
    round_number=8,
    driver="VER",
    session_part="Q3"
)

print(result["driver"])
print(result["lapTime"])
print(result["sampleCount"])

print(result["telemetry"][0])
print(result["telemetry"][-1])