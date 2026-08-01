import fastf1
import pandas as pd
from pathlib import Path

YEAR = 2024
ROUND = 10  # Spain
DRIVER = "VER"
LAP_NUMBER = 11


def compute_session_thresholds(session):
    all_speed = []
    all_rpm = []

    print("Collecting telemetry from all laps...")

    for _, lap in session.laps.iterrows():
        try:
            tel = lap.get_car_data().add_distance()

            if tel.empty:
                continue

            all_speed.extend(tel["Speed"].dropna().tolist())
            all_rpm.extend(tel["RPM"].dropna().tolist())

        except Exception:
            pass

    speed = pd.Series(all_speed)
    rpm = pd.Series(all_rpm)

    return {
        "speed50": speed.quantile(0.50),
        "speed75": speed.quantile(0.75),
        "speed90": speed.quantile(0.90),
        "speed95": speed.quantile(0.95),
        "speed99": speed.quantile(0.99),
        "rpm75": rpm.quantile(0.75),
        "rpm90": rpm.quantile(0.90),
        "rpm95": rpm.quantile(0.95),
    }


def classify(row, thresholds):
    speed = row.Speed
    throttle = row.Throttle
    brake = row.Brake
    rpm = row.RPM
    gear = row.nGear
    accel = row.Acceleration

    reason = ""

    if brake:
        return "BRAKE", "Brake=True"

    if (
        throttle == 0
        and speed > thresholds["speed50"]
        and accel > -2
    ):
        return "LIFT", "Throttle=0"

    if (
        throttle == 0
        and speed <= thresholds["speed50"]
    ):
        return "ROLLING", "Throttle=0 LowSpeed"

    if (
        throttle >= 99
        and gear >= 7
        and speed >= thresholds["speed90"]
        and accel < 0.3
    ):
        return "CLIPPING", "HighSpeed LowAccel"

    if throttle >= 99:
        return "FULL", "Throttle=100"

    return "CORNER", "Default"


def main():
    fastf1.Cache.enable_cache("cache")

    session = fastf1.get_session(YEAR, ROUND, "R")
    session.load()

    thresholds = compute_session_thresholds(session)

    print()
    print("Thresholds")
    print(thresholds)

    lap = session.laps.pick_drivers(DRIVER).pick_laps(LAP_NUMBER).iloc[0]

    tel = lap.get_car_data().add_distance()

    tel = tel.copy()

    tel["DeltaSeconds"] = tel["Time"].dt.total_seconds().diff()
    tel["DeltaSpeed"] = tel["Speed"].diff()

    tel["Acceleration"] = (
        tel["DeltaSpeed"] / 3.6
    ) / tel["DeltaSeconds"]

    tel["Acceleration"] = tel["Acceleration"].fillna(0)

    classifications = []
    reasons = []

    for _, row in tel.iterrows():
        c, r = classify(row, thresholds)
        classifications.append(c)
        reasons.append(r)

    tel["Classification"] = classifications
    tel["Reason"] = reasons

    columns = [
        "Time",
        "Distance",
        "Speed",
        "Throttle",
        "Brake",
        "RPM",
        "nGear",
        "DeltaSeconds",
        "DeltaSpeed",
        "Acceleration",
        "Classification",
        "Reason",
    ]

    output = tel[columns]

    filename = f"{DRIVER}_lap_{LAP_NUMBER}_analysis.xlsx"

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        output.to_excel(writer, sheet_name="Telemetry", index=False)

        pd.DataFrame(
            {
                "Metric": list(thresholds.keys()),
                "Value": list(thresholds.values()),
            }
        ).to_excel(writer, sheet_name="Thresholds", index=False)

    print()
    print(f"Exported -> {Path(filename).resolve()}")


if __name__ == "__main__":
    main()