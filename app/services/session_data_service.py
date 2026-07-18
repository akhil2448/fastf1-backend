import pandas as pd
from app.utils.time_utils import convert_all_timedelta_columns
from app.services.race_management.tyre_compound_service import (TyreCompoundService,)

tyre_compound_service = TyreCompoundService()

## DEAD CODE - NOT USING THIS ANYMORE

def load_race_laps_and_weather(session):
    """
    Loads, joins, cleans and time-converts lap + weather data.
    """

    session.load(laps=True, telemetry=True, weather=True)

    laps = session.laps.reset_index(drop=True)
    weather = session.laps.get_weather_data().reset_index(drop=True)

    joined = pd.concat(
        [laps, weather.loc[:, weather.columns != "Time"]],
        axis=1
    )

    joined = joined[
        [
            "DriverNumber", "Driver", "Team",
            "LapNumber", "LapTime", "IsPersonalBest",
            "PitInTime", "PitOutTime",
            "Time", "LapStartTime",
            "Position", "Compound", "TyreLife",
            "TrackStatus"
        ]
    ]
    
    joined["Compound"] = joined["Compound"].apply(tyre_compound_service.normalize)

    joined = convert_all_timedelta_columns(joined)

    return joined
