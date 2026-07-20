from app.services.session_cache_service import get_loaded_session

YEAR = 2024
ROUND = 11

##############################################################

session = get_loaded_session(
    YEAR,
    ROUND,
)

circuit = session.get_circuit_info()

##############################################################
# General
##############################################################

print()
print("=" * 80)
print("CIRCUIT INFO")
print("=" * 80)

print()

print("Circuit object:")
print(type(circuit))

print()

##############################################################
# Corners
##############################################################

print("=" * 80)
print("CORNERS")
print("=" * 80)

print()

print("Type:")
print(type(circuit.corners))

print()

print("Columns:")
print(list(circuit.corners.columns))

print()

print("Shape:")
print(circuit.corners.shape)

print()

print("First 25 rows")
print("-" * 80)

print(
    circuit.corners.head(25)
)

print()

##############################################################
# Marshal lights
##############################################################

print("=" * 80)
print("MARSHAL LIGHTS")
print("=" * 80)

print()

if hasattr(circuit, "marshal_lights"):

    print(type(circuit.marshal_lights))

    if circuit.marshal_lights is not None:

        try:
            print(list(circuit.marshal_lights.columns))
            print()
            print(circuit.marshal_lights.head())
        except Exception:
            print(circuit.marshal_lights)

else:

    print("Not available")

print()

##############################################################
# Marshal sectors
##############################################################

print("=" * 80)
print("MARSHAL SECTORS")
print("=" * 80)

print()

if hasattr(circuit, "marshal_sectors"):

    print(type(circuit.marshal_sectors))

    if circuit.marshal_sectors is not None:

        try:
            print(list(circuit.marshal_sectors.columns))
            print()
            print(circuit.marshal_sectors.head())
        except Exception:
            print(circuit.marshal_sectors)

else:

    print("Not available")

print()

##############################################################
# Full object
##############################################################

print("=" * 80)
print("DIR(circuit)")
print("=" * 80)

print()

print(dir(circuit))