import pprint

from app.services.session_cache_service import (
    get_loaded_qualifying_session
)

YEAR = 2020
ROUND = 3

session = get_loaded_qualifying_session(
    YEAR,
    ROUND
)

print("\n==============================")
print("SESSION INFO")
print("==============================")

print(session.event['EventName'])

print("\n==============================")
print("LAPS COLUMNS")
print("==============================")

for col in session.laps.columns:
    print(col)

print("\n==============================")
print("RESULTS COLUMNS")
print("==============================")

for col in session.results.columns:
    print(col)

print("\n==============================")
print("FIRST 5 LAPS")
print("==============================")

print(
    session.laps.head()
)

print("\n==============================")
print("FIRST 5 RESULTS")
print("==============================")

print(
    session.results.head()
)