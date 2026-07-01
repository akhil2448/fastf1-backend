import pandas as pd

from .models import LapAnalysisResult
from .tyre_compound_service import TyreCompoundService


class LapAnalyzer:

    INVALID_TRACK_STATUS = {
        "2",   # Yellow
        "4",   # Safety Car
        "5",   # Red Flag
        "6",   # VSC
        "7",   # VSC Ending
    }
    
    def __init__(self):
        self.compound_service = TyreCompoundService()

    def analyze(self, lap) -> LapAnalysisResult:

        reasons = []

        ##############################################################
        # Race start
        ##############################################################

        if int(lap["LapNumber"]) == 1:
            reasons.append("Race start")

        ##############################################################
        # Pit in
        ##############################################################

        if pd.notna(lap["PitInTime"]):
            reasons.append("Pit in lap")

        ##############################################################
        # Pit out
        ##############################################################

        if pd.notna(lap["PitOutTime"]):
            reasons.append("Out lap")

        ##############################################################
        # Accurate
        ##############################################################

        if not lap["IsAccurate"]:
            reasons.append("FastF1 marked lap as inaccurate")

        ##############################################################
        # Track status
        ##############################################################

        track_status = str(lap["TrackStatus"])

        active_flags = set(track_status)

        if active_flags.intersection(self.INVALID_TRACK_STATUS):

            if "2" in active_flags:
                reasons.append("Yellow flag")

            if "4" in active_flags:
                reasons.append("Safety Car")

            if "5" in active_flags:
                reasons.append("Red Flag")

            if "6" in active_flags:
                reasons.append("Virtual Safety Car")

            if "7" in active_flags:
                reasons.append("Virtual Safety Car Ending")

        ##############################################################
        # Tyre compound
        ##############################################################

        compound = lap["Compound"]

        if not self.compound_service.is_valid(compound):
            reasons.append("Missing tyre compound")

        ##############################################################

        return LapAnalysisResult(
            valid=len(reasons) == 0,
            reasons=reasons,
        )
