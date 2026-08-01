from pathlib import Path

import fastf1
import pandas as pd

YEAR = 2024
ROUND = 10
SESSION = "R"

DRIVER = "VER"
LAP_NUMBER = 11

WINDOW_METERS = 120


def main():
    print("=" * 80)
    print("Loading session...")
    print("=" * 80)

    session = fastf1.get_session(YEAR, ROUND, SESSION)
    session.load()

    lap = (
        session.laps
        .pick_drivers(DRIVER)
        .pick_laps(LAP_NUMBER)
        .iloc[0]
    )

    car = lap.get_car_data().add_distance()
    pos = lap.get_pos_data()

    telemetry = pd.merge_asof(
        car.sort_values("Time"),
        pos.sort_values("Time"),
        on="Time",
        direction="nearest",
    )

    circuit = session.get_circuit_info()

    corners = circuit.corners.copy()

    corners = corners.sort_values("Distance").reset_index(drop=True)

    writer = pd.ExcelWriter(
        Path.cwd() / f"{DRIVER}_lap_{LAP_NUMBER}_corner_analysis.xlsx",
        engine="openpyxl",
    )

    print()
    print("=" * 80)
    print("Corner Behaviour")
    print("=" * 80)

    for _, corner in corners.iterrows():

        d = float(corner.Distance)

        number = int(corner.Number)

        letter = corner.Letter if pd.notna(corner.Letter) else ""

        start = max(0, d - WINDOW_METERS)

        end = d + WINDOW_METERS

        samples = telemetry[
            (telemetry.Distance >= start)
            & (telemetry.Distance <= end)
        ].copy()

        samples["CornerDistance"] = d
        samples["Offset"] = samples.Distance - d

        samples = samples[
            [
                "Distance",
                "Offset",
                "Speed",
                "Throttle",
                "Brake",
                "RPM",
                "nGear",
                "X",
                "Y",
            ]
        ]

        print(
            f"T{number}{letter:<2}"
            f"  Distance={d:7.1f}m"
            f"   Samples={len(samples)}"
        )

        sheet = f"T{number}{letter}"

        samples.to_excel(writer, sheet_name=sheet[:31], index=False)

    writer.close()

    print()
    print("=" * 80)
    print("Excel exported.")
    print("=" * 80)


if __name__ == "__main__":
    main()