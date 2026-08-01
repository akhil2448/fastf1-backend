from collections import Counter

import fastf1

YEAR = 2024
ROUND = 10
DRIVER = "VER"
LAP_NUMBER = 11


def pct(count, total):
    return round(100 * count / total, 1)


fastf1.Cache.enable_cache("cache")

session = fastf1.get_session(YEAR, ROUND, "R")
session.load()

lap = (
    session.laps
    .pick_drivers(DRIVER)
    .pick_laps(LAP_NUMBER)
    .iloc[0]
)

telemetry = lap.get_car_data().add_distance()

total = len(telemetry)

counter = Counter()

gear_shifts = 0
previous_gear = None

for _, row in telemetry.iterrows():

    throttle = float(row["Throttle"])
    brake = bool(row["Brake"])
    speed = float(row["Speed"])
    rpm = float(row["RPM"])
    gear = int(row["nGear"])

    if previous_gear is not None and gear != previous_gear:
        gear_shifts += 1

    previous_gear = gear

    if brake:
        counter["brake"] += 1
        continue

    if throttle >= 99:
        if gear >= 7 and speed > 250 and rpm < 10800:
            counter["clipping"] += 1
        else:
            counter["full"] += 1
        continue

    if throttle == 0 and speed > 120:
        counter["lift"] += 1
        continue

    if 0 < throttle < 15:
        counter["rolling"] += 1
        continue

    counter["cornering"] += 1


print()
print("=" * 70)
print(f"{DRIVER} - Lap {LAP_NUMBER}")
print("=" * 70)

print(f"Lap Time      : {lap['LapTime']}")
print(f"Compound      : {lap['Compound']}")
print(f"Tyre Life     : {lap['TyreLife']}")
print(f"Stint         : {lap['Stint']}")
print()

print(f"Max Speed     : {telemetry['Speed'].max():.1f} km/h")
print(f"Min Speed     : {telemetry['Speed'].min():.1f} km/h")
print(f"Avg Speed     : {telemetry['Speed'].mean():.1f} km/h")
print(f"Gear Shifts   : {gear_shifts}")
print()

print("Distribution")
print("-" * 70)
print(f"Full Throttle : {pct(counter['full'], total):5.1f}%")
print(f"Brake         : {pct(counter['brake'], total):5.1f}%")
print(f"Lift & Coast  : {pct(counter['lift'], total):5.1f}%")
print(f"Rolling       : {pct(counter['rolling'], total):5.1f}%")
print(f"Clipping      : {pct(counter['clipping'], total):5.1f}%")
print(f"Cornering     : {pct(counter['cornering'], total):5.1f}%")

print("-" * 70)
print(
    f"Total         : "
    f"{pct(sum(counter.values()), total):5.1f}%"
)