from app.services.race_management.race_gap_calculator import (
    RaceGapCalculator,
)

calculator = RaceGapCalculator()

tests = [

    (
        "Same lap",
        21, 0.62,
        21, 0.67,
    ),

    (
        "Ahead after S/F",
        21, 0.98,
        22, 0.02,
    ),

    (
        "Behind before S/F",
        22, 0.03,
        21, 0.98,
    ),

    (
        "One full lap ahead",
        20, 0.50,
        21, 0.55,
    ),

    (
        "One full lap behind",
        21, 0.60,
        20, 0.55,
    ),
]

for name, cl, cp, ol, op in tests:

    gap = calculator.calculate_gap(
        cl,
        cp,
        ol,
        op,
    )

    print(f"{name:<25} {gap:+.3f}")