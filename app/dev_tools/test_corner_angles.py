from app.services.session_cache_service import get_loaded_session

YEAR = 2024
ROUND = 11

session = get_loaded_session(
    YEAR,
    ROUND,
)

corners = session.get_circuit_info().corners

print()

print("=" * 90)
print("CORNERS")
print("=" * 90)

for _, corner in corners.iterrows():

    print(

        f"T{corner['Number']:>2}"
        f"{corner['Letter']:<2}"

        f"  Angle={corner['Angle']:>8.2f}"

        f"  Distance={corner['Distance']:>8.1f}"

    )