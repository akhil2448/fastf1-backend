from __future__ import annotations

import fastf1

CACHE_DIR = "cache"

YEAR = 2023
ROUND = 22
SESSION = "R"


def main():

    fastf1.Cache.enable_cache(CACHE_DIR)

    session = fastf1.get_session(
        YEAR,
        ROUND,
        SESSION,
    )

    session.load()

    circuit = session.get_circuit_info()

    print()
    print("=" * 100)
    print("CircuitInfo Object")
    print("=" * 100)
    print()

    print(type(circuit))

    print()

    print("=" * 100)
    print("Available Attributes")
    print("=" * 100)
    print()

    for name in sorted(vars(circuit).keys()):
        print(name)

    print()

    print("=" * 100)
    print("Attribute Types")
    print("=" * 100)
    print()

    for name, value in vars(circuit).items():

        print(f"{name:<20} {type(value)}")

    print()

    print("=" * 100)
    print("Corners")
    print("=" * 100)
    print()

    print(circuit.corners)

    print()

    print("=" * 100)
    print("Marshal Lights")
    print("=" * 100)
    print()

    if hasattr(circuit, "marshal_lights"):
        print(circuit.marshal_lights)

    print()

    print("=" * 100)
    print("Marshal Sectors")
    print("=" * 100)
    print()

    if hasattr(circuit, "marshal_sectors"):
        print(circuit.marshal_sectors)

    print()

    print("=" * 100)
    print("Rotation")
    print("=" * 100)
    print()

    if hasattr(circuit, "rotation"):
        print(circuit.rotation)

    print()

    print("=" * 100)
    print("Corner Columns")
    print("=" * 100)
    print()

    for column in circuit.corners.columns:
        print(column)


if __name__ == "__main__":
    main()