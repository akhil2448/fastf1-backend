from app.services.session_cache_service import (
    get_loaded_qualifying_session
)

session = get_loaded_qualifying_session(
    2021,
    8
)

driver = "VER"

result = session.results.loc[
    session.results["Abbreviation"] == driver
].iloc[0]

q3_time = result["Q3"]

lap = (
    session.laps
    .pick_drivers(driver)
    .loc[lambda df: df["LapTime"] == q3_time]
    .iloc[0]
)

telemetry = lap.get_telemetry()

print("\n===================")
print("TELEMETRY COLUMNS")
print("===================")

for col in telemetry.columns:
    print(col)

print("\n===================")
print("ROWS")
print("===================")

print(len(telemetry))

print("\n===================")
print("HEAD")
print("===================")

print(
    telemetry.head()
)


telemetry = lap.get_telemetry()

print(
    telemetry[
        [
            "Distance",
            "RelativeDistance",
            "Time"
        ]
    ].tail()
)

print("\n===================")
print("TIME DELTAS")
print("===================")

time_seconds = (
    telemetry["Time"]
    .dt.total_seconds()
)

print(
    time_seconds.diff().describe()
)