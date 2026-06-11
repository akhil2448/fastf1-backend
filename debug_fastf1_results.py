# debug_fastf1_results.py

import fastf1
import pandas as pd

YEAR = 2020
ROUND = 3

session = fastf1.get_session(YEAR, ROUND, "R")
session.load()

results = session.results

print("\n================ RAW RESULTS DF ================\n")

# show all columns
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 2000)

print(results)

print("\n================ COLUMN TYPES ================\n")

print(results.dtypes)

print("\n================ DRIVER RESULTS ================\n")

for _, row in results.iterrows():

    print("--------------------------------------------------")

    print("Driver:", row["Abbreviation"])

    print("Position:", row["Position"])

    print("Status:", row["Status"])

    print("GridPosition:", row.get("GridPosition"))

    print("Points:", row.get("Points"))

    print("Laps:", row.get("Laps"))

    print("Time:", row.get("Time"))

    print("Time type:", type(row.get("Time")))

    print("GapToLeader:", row.get("GapToLeader"))

    print("GapToLeader type:", type(row.get("GapToLeader")))

    print("IntervalToPositionAhead:", row.get("IntervalToPositionAhead"))

    print(
        "IntervalToPositionAhead type:",
        type(row.get("IntervalToPositionAhead"))
    )

    print("ClassifiedPosition:", row.get("ClassifiedPosition"))

    print("Full row dict:")

    print(row.to_dict())

print("\n================ AVAILABLE COLUMNS ================\n")

print(list(results.columns))