"""
app/dev_tools/analyze_track_model.py

Explore FastF1 circuit information and compare it with telemetry.

Outputs:
- Console summary
- Excel workbook:
    1. CircuitInfo
    2. Straights
    3. Telemetry
"""

from pathlib import Path

import pandas as pd
import fastf1

YEAR = 2024
ROUND = 10
DRIVER = "VER"
LAP_NUMBER = 11


def main():
    print("\n" + "=" * 80)
    print("Loading session...")
    print("=" * 80)

    session = fastf1.get_session(YEAR, ROUND, "R")
    session.load()

    circuit = session.get_circuit_info()

    print("\nCircuit loaded.")

    print(f"Rotation : {circuit.rotation:.1f}°")

    print(f"Corners  : {len(circuit.corners)}")

    print(f"Marshal sectors : {len(circuit.marshal_sectors)}")

    print(f"Marshal lights  : {len(circuit.marshal_lights)}")

    print()

    # ---------------------------------------------------------
    # Corner table
    # ---------------------------------------------------------

    corners = circuit.corners.copy()

    if "Distance" in corners.columns:
        corners = corners.sort_values("Distance").reset_index(drop=True)

    print("=" * 80)
    print("Corners")
    print("=" * 80)

    for _, row in corners.iterrows():
        number = row["Number"]
        letter = row["Letter"] if pd.notna(row["Letter"]) else ""

        distance = row.get("Distance", None)

        if pd.isna(distance):
            distance_text = "N/A"
        else:
            distance_text = f"{distance:.1f} m"

        print(
            f"T{number}{letter:<2} "
            f"Distance={distance_text:<10} "
            f"Angle={row['Angle']:>6.1f}"
        )

    # ---------------------------------------------------------
    # Straights
    # ---------------------------------------------------------

    straight_rows = []

    print()
    print("=" * 80)
    print("Straights")
    print("=" * 80)

    if "Distance" in corners.columns:

        for i in range(len(corners) - 1):

            start = corners.iloc[i]
            end = corners.iloc[i + 1]

            length = end.Distance - start.Distance

            straight_rows.append(
                {
                    "From Corner": f"{int(start.Number)}{start.Letter or ''}",
                    "To Corner": f"{int(end.Number)}{end.Letter or ''}",
                    "Start Distance": start.Distance,
                    "End Distance": end.Distance,
                    "Straight Length": length,
                }
            )

            print(
                f"T{int(start.Number)} -> "
                f"T{int(end.Number)} : "
                f"{length:.1f} m"
            )

    straights_df = pd.DataFrame(straight_rows)

    # ---------------------------------------------------------
    # Telemetry
    # ---------------------------------------------------------

    lap = session.laps.pick_drivers(DRIVER).pick_laps(LAP_NUMBER).iloc[0]

    car = lap.get_car_data().add_distance()
    
    print("\nCAR DATA COLUMNS")
    print(car.columns.tolist())

    print("\nPOSITION DATA COLUMNS")
    print(lap.get_pos_data().columns.tolist())
    
    pos = lap.get_pos_data()

    # Merge on telemetry time
    telemetry = pd.merge_asof(
        car.sort_values("Time"),
        pos.sort_values("Time"),
        on="Time",
        direction="nearest"
    )

    telemetry = telemetry[
        [
            "Time",
            "Distance",
            "Speed",
            "Throttle",
            "Brake",
            "RPM",
            "nGear",
            "X",
            "Y",
        ]
    ].copy()

    print()
    print("=" * 80)
    print("Telemetry")
    print("=" * 80)

    print(telemetry.head(20))

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    filename = Path.cwd() / f"{DRIVER}_lap_{LAP_NUMBER}_track_model.xlsx"

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:

        corners.to_excel(writer, sheet_name="CircuitInfo", index=False)

        straights_df.to_excel(writer, sheet_name="Straights", index=False)

        telemetry.to_excel(writer, sheet_name="Telemetry", index=False)

    print()
    print("=" * 80)
    print(f"Exported: {filename}")
    print("=" * 80)


if __name__ == "__main__":
    main()