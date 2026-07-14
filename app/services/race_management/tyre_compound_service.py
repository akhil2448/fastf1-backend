from typing import Optional


class TyreCompoundService:
    """
    Normalizes historical Pirelli compounds into their modern
    comparison families.

    Historical name is preserved elsewhere if needed for display.
    """

    _NORMALIZATION_MAP = {
        # Soft family
        "HYPERSOFT": "SOFT",
        "ULTRASOFT": "SOFT",
        "SUPERSOFT": "SOFT",
        "SOFT": "SOFT",

        # Medium family
        "MEDIUM": "MEDIUM",

        # Hard family
        "HARD": "HARD",
        "SUPERHARD": "HARD",

        # Wet compounds
        "INTERMEDIATE": "INTERMEDIATE",
        "WET": "WET",

        # Unknown
        "UNKNOWN": "UNKNOWN",
    }

    _INVALID_VALUES = {
        "",
        "NONE",
        "NAN",
    }
    
    # TODO:
    # These are reference tyre lifespans used only for lap comparison.
    # They are not intended to represent actual stint lengths, which vary
    # by circuit, weather, safety cars and strategy.
    _REFERENCE_TYRE_LIFE = {

        "SOFT": 20,

        "MEDIUM": 30,

        "HARD": 40,

        "INTERMEDIATE": 25,

        "WET": 20,
    }
    
    def reference_life(
        self,
        compound: Optional[str],
    ) -> int:

        compound = self.normalize(compound)

        return self._REFERENCE_TYRE_LIFE.get(
            compound,
            30,
        )

    def normalize(self, compound: Optional[str]) -> Optional[str]:

        if compound is None:
            return None

        compound = str(compound).strip().upper()

        if compound in self._INVALID_VALUES:
            return None

        return self._NORMALIZATION_MAP.get(
            compound,
            compound
        )

    def is_valid(self, compound: Optional[str]) -> bool:
        return self.normalize(compound) is not None

    def is_dry(self, compound: Optional[str]) -> bool:

        compound = self.normalize(compound)

        return compound in {
            "SOFT",
            "MEDIUM",
            "HARD",
        }

    def is_wet(self, compound: Optional[str]) -> bool:

        compound = self.normalize(compound)

        return compound in {
            "INTERMEDIATE",
            "WET",
        }