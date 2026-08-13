from __future__ import annotations

import fastf1
import pandas as pd

CACHE_DIR = "cache"

YEAR = 2023
ROUND = 22
SESSION = "R"


def print_header(title: str):

    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


def main():

    fastf1.Cache.enable_cache(CACHE_DIR)

    session = fastf1.get_session(
        YEAR,
        ROUND,
        SESSION,
    )

    session.load()

    circuit = session.get_circuit_info()

    #
    # CircuitInfo object
    #
    print_header("CircuitInfo Object")

    print(circuit)

    #
    # Available attributes
    #
    print_header("Available Attributes")

    for attribute in sorted(dir(circuit)):

        if attribute.startswith("_"):
            continue

        print(attribute)

    #
    # Corners
    #
    print_header("Corners")

    if hasattr(circuit, "corners"):

        corners = circuit.corners

        print(f"Rows    : {len(corners)}")
        print(f"Columns : {len(corners.columns)}")

        print("\nColumns")

        for column in corners.columns:
            print(f"  {column}")

        print("\nDtypes")

        print(corners.dtypes)

        print("\nData")

        with pd.option_context(
            "display.max_rows", None,
            "display.max_columns", None,
            "display.width", None,
        ):
            print(corners)

    #
    # Marshal Lights
    #
    print_header("Marshal Lights")

    if hasattr(circuit, "marshal_lights"):

        lights = circuit.marshal_lights

        print(f"Rows    : {len(lights)}")
        print(f"Columns : {len(lights.columns)}")

        print("\nColumns")

        for column in lights.columns:
            print(f"  {column}")

        print("\nData")

        with pd.option_context(
            "display.max_rows", None,
            "display.max_columns", None,
            "display.width", None,
        ):
            print(lights)

    #
    # Marshal Sectors
    #
    print_header("Marshal Sectors")

    if hasattr(circuit, "marshal_sectors"):

        sectors = circuit.marshal_sectors

        print(f"Rows    : {len(sectors)}")
        print(f"Columns : {len(sectors.columns)}")

        print("\nColumns")

        for column in sectors.columns:
            print(f"  {column}")

        print("\nData")

        with pd.option_context(
            "display.max_rows", None,
            "display.max_columns", None,
            "display.width", None,
        ):
            print(sectors)

    #
    # Rotation
    #
    print_header("Track Rotation")

    if hasattr(circuit, "rotation"):

        print(circuit.rotation)


if __name__ == "__main__":
    main()