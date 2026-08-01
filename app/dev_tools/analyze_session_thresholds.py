from collections import Counter

import fastf1
import numpy as np
import pandas as pd

YEAR = 2024
ROUND = 10
TARGET_DRIVER = "VER"
TARGET_LAP = 11


def percentile(series, p):
    return float(np.percentile(series, p))


fastf1.Cache.enable_cache("Cache")

session = fastf1.get_session(YEAR, ROUND, "R")
session.load()

print()
print("=" * 80)
print("Building session statistics...")
print("=" * 80)

all_speed = []
all_rpm = []

lap_count = 0

for _, lap in session.laps.iterrows():

    if pd.isna(lap["LapTime"]):
        continue

    if lap["PitInTime"] is not pd.NaT:
        continue

    if lap["PitOutTime"] is not pd.NaT:
        continue

    telemetry = lap.get_car_data()

    if telemetry.empty:
        continue

    all_speed.extend(telemetry["Speed"].tolist())
    all_rpm.extend(telemetry["RPM"].tolist())

    lap_count += 1

stats = {
    "speed50": percentile(all_speed, 50),
    "speed75": percentile(all_speed, 75),
    "speed90": percentile(all_speed, 90),
    "speed95": percentile(all_speed, 95),

    "rpm75": percentile(all_rpm, 75),
    "rpm90": percentile(all_rpm, 90),
    "rpm95": percentile(all_rpm, 95),
}

print()
print(f"Laps analysed : {lap_count}")
print()

print("Speed Percentiles")
print("-----------------")
for k in ("speed50", "speed75", "speed90", "speed95"):
    print(f"{k:10} {stats[k]:6.1f}")

print()

print("RPM Percentiles")
print("----------------")
for k in ("rpm75", "rpm90", "rpm95"):
    print(f"{k:10} {stats[k]:7.0f}")

print()

print("=" * 80)
print(f"Applying thresholds to {TARGET_DRIVER} Lap {TARGET_LAP}")
print("=" * 80)

lap = (
    session.laps
    .pick_drivers(TARGET_DRIVER)
    .pick_laps(TARGET_LAP)
    .iloc[0]
)

telemetry = lap.get_car_data()

counter = Counter()

examples = []

for _, row in telemetry.iterrows():

    throttle = float(row["Throttle"])
    brake = bool(row["Brake"])
    speed = float(row["Speed"])
    rpm = float(row["RPM"])
    gear = int(row["nGear"])

    if brake:
        cls = "BRAKE"

    elif (
        throttle >= 99
        and speed >= stats["speed95"]
        and rpm <= stats["rpm90"]
        and gear >= 7
    ):
        cls = "CLIPPING"

    elif throttle >= 99:
        cls = "FULL"

    elif (
        throttle == 0
        and brake is False
        and speed >= stats["speed75"]
        and gear >= 6
    ):
        cls = "LIFT"

    elif (
        0 < throttle < 15
        and brake is False
    ):
        cls = "ROLLING"

    else:
        cls = "CORNER"

    counter[cls] += 1

    examples.append({
        "time": row["Time"],
        "speed": speed,
        "rpm": rpm,
        "gear": gear,
        "throttle": throttle,
        "brake": brake,
        "class": cls,
    })

print()
print("Distribution")
print("------------------------------")

total = len(examples)

for c in [
    "FULL",
    "BRAKE",
    "LIFT",
    "ROLLING",
    "CLIPPING",
    "CORNER",
]:
    pct = counter[c] * 100 / total
    print(f"{c:10} {counter[c]:4d} ({pct:5.1f}%)")

print()
print("=" * 80)
print("First 40 classified samples")
print("=" * 80)

for row in examples[:40]:
    print(
        f"{str(row['time'])[7:15]:>9} | "
        f"{row['class']:9} | "
        f"{row['speed']:6.1f} | "
        f"{row['rpm']:7.0f} | "
        f"G{row['gear']} | "
        f"T{row['throttle']:5.1f}"
    )