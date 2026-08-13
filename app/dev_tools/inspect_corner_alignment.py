from __future__ import annotations

import fastf1
import pandas as pd


YEAR = 2023
ROUND = 22
DRIVER = "VER"
LAP_NUMBER = 1


def main():

    session = fastf1.get_session(YEAR, ROUND, "R")
    session.load()

    lap = (
        session.laps
        .pick_drivers(DRIVER)
        .pick_laps(LAP_NUMBER)
        .iloc[0]
    )

    telemetry = lap.get_telemetry().copy()

    corners = session.get_circuit_info().corners.copy()

    print()
    print("=" * 100)
    print("Corner Alignment")
    print("=" * 100)

    print()

    for _, corner in corners.iterrows():

        apex_distance = float(corner["Distance"])

        telemetry["DistanceDiff"] = (
            telemetry["Distance"] - apex_distance
        ).abs()

        nearest = telemetry.loc[
            telemetry["DistanceDiff"].idxmin()
        ]

        print(
            f"Turn {corner['Number']}{corner['Letter'] or ''}"
        )

        print(
            f"  Official Apex Distance : {apex_distance:.3f} m"
        )

        print(
            f"  Telemetry Distance     : {nearest['Distance']:.3f} m"
        )

        print(
            f"  Difference             : {nearest['DistanceDiff']:.3f} m"
        )

        print(
            f"  Speed                  : {nearest['Speed']:.1f} km/h"
        )

        print(
            f"  Throttle              : {nearest['Throttle']:.0f}%"
        )

        print(
            f"  Brake                 : {nearest['Brake']}"
        )

        print(
            f"  Gear                  : {nearest['nGear']}"
        )

        print(
            f"  X,Y                   : ({nearest['X']:.2f}, {nearest['Y']:.2f})"
        )

        print()


if __name__ == "__main__":
    main()