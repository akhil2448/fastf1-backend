from dataclasses import dataclass


@dataclass(frozen=True)
class WakeProfile:

    name: str

    full_distance: float
    full_weight: float

    medium_distance: float
    medium_weight: float

    light_distance: float
    light_weight: float

    maximum_distance: float
    maximum_weight: float
    

HIGH_OUTWASH = WakeProfile(

    name="High Outwash",

    full_distance=40,
    full_weight=1.00,

    medium_distance=80,
    medium_weight=0.80,

    light_distance=120,
    light_weight=0.50,

    maximum_distance=180,
    maximum_weight=0.20,
)

GROUND_EFFECT_V1 = WakeProfile(

    name="Ground Effect V1",

    full_distance=35,
    full_weight=1.00,

    medium_distance=65,
    medium_weight=0.72,

    light_distance=100,
    light_weight=0.38,

    maximum_distance=150,
    maximum_weight=0.12,
)

GROUND_EFFECT_MATURE = WakeProfile(

    name="Ground Effect Mature",

    full_distance=32,
    full_weight=1.00,

    medium_distance=60,
    medium_weight=0.65,

    light_distance=90,
    light_weight=0.30,

    maximum_distance=135,
    maximum_weight=0.08,
)

ACTIVE_AERO_2026 = WakeProfile(

    name="Active Aero",

    full_distance=28,
    full_weight=1.00,

    medium_distance=52,
    medium_weight=0.58,

    light_distance=78,
    light_weight=0.20,

    maximum_distance=115,
    maximum_weight=0.03,
)


WAKE_PROFILES = {

    2018: HIGH_OUTWASH,
    2019: HIGH_OUTWASH,
    2020: HIGH_OUTWASH,
    2021: HIGH_OUTWASH,

    2022: GROUND_EFFECT_V1,

    2023: GROUND_EFFECT_MATURE,
    2024: GROUND_EFFECT_MATURE,
    2025: GROUND_EFFECT_MATURE,
    
    2026: ACTIVE_AERO_2026,
}