import pandas as pd

from .lap_analyzer import LapAnalyzer
from .tyre_compound_service import TyreCompoundService
from .models import (
    AnalyzedLap,
    StintAnalysisResult,
)


class StintAnalyzer:

    def __init__(self):

        self.lap_analyzer = LapAnalyzer()

        self.compound_service = TyreCompoundService()

    def analyze(
        self,
        driver_laps,
        driver_number,
        driver_code,
    ):

        results = []

        grouped = driver_laps.groupby("Stint")

        for stint_number, stint_df in grouped:

            first = stint_df.iloc[0]
            last = stint_df.iloc[-1]

            stint = StintAnalysisResult(
                stint=int(stint_number),
                compound=first["Compound"],
                tyre_life_start=int(first["TyreLife"]),
                tyre_life_end=int(last["TyreLife"]),
                start_lap=int(first["LapNumber"]),
                end_lap=int(last["LapNumber"]),
                total_laps=len(stint_df),
            )

            for _, lap in stint_df.iterrows():

                analysis = self.lap_analyzer.analyze(lap)

                analyzed_lap = AnalyzedLap(
                    
                    driver_number=driver_number,

                    driver_code=driver_code,

                    lap_number=int(lap["LapNumber"]),

                    stint=int(lap["Stint"]),

                    compound=lap["Compound"],

                    normalized_compound=self.compound_service.normalize(
                        lap["Compound"]
                    ),

                    tyre_life=int(lap["TyreLife"]),

                    fresh_tyre=bool(lap["FreshTyre"]),

                    lap_time=lap["LapTime"],

                    lap_start_time=lap["LapStartTime"],

                    lap_end_time=lap["Time"],

                    sector1_time=lap["Sector1Time"],

                    sector2_time=lap["Sector2Time"],

                    sector3_time=lap["Sector3Time"],

                    position=(
                        None
                        if pd.isna(lap["Position"])
                        else int(lap["Position"])
                    ),

                    track_status=str(lap["TrackStatus"]),

                    deleted=bool(lap["Deleted"]),

                    speed_i1=float(lap["SpeedI1"]),

                    speed_i2=float(lap["SpeedI2"]),

                    speed_fl=float(lap["SpeedFL"]),

                    speed_st=float(lap["SpeedST"]),

                    analysis=analysis,
                )

                stint.analyzed_laps.append(analyzed_lap)

            results.append(stint)

        return results