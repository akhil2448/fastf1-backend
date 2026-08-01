from __future__ import annotations

from typing import Any

import pandas as pd

from app.services.race_management.race_analyzer.race_metadata_builder import RaceMetadataBuilder
from app.services.team_normalizer import normalize_team_name
from app.services.race_management.tyre_compound_service import TyreCompoundService


class RaceAnalyzerService:
    """
    Builds Race Analyzer data for one or two selected drivers.
    """

    MAX_DRIVERS = 2
    
    _COMPOUNDS = TyreCompoundService()

    @classmethod
    def build(
        cls,
        session,
        drivers: list[str],
    ) -> dict[str, Any]:

        if not drivers:
            raise ValueError("At least one driver must be selected.")

        drivers = [d.upper() for d in drivers]

        if len(drivers) > cls.MAX_DRIVERS:
            raise ValueError("Maximum two drivers are supported.")

        reference_driver = drivers[0]

        return {
            "race": cls._build_race(session),

            "referenceDriver": reference_driver,

            "trackMetadata": RaceMetadataBuilder.build(
                session=session,
                reference_driver=reference_driver,
            ),

            "drivers": [
                cls._build_driver(session, driver)
                for driver in drivers
            ],
        }

    @classmethod
    def _build_driver(
        cls,
        session,
        driver: str,
    ) -> dict[str, Any]:

        laps = session.laps.pick_drivers(driver)

        if laps.empty:
            raise ValueError(f"No laps found for driver '{driver}'")

        info = laps.iloc[0]
        
        metadata = cls._driver_metadata(session, driver)

        return {
            "driver": driver,
            "driverNumber": str(info.DriverNumber),

            "fullName": metadata["fullName"],
            "headshotUrl": metadata["headshotUrl"],
            "countryCode": metadata["countryCode"],
            
            "teamName": normalize_team_name(info.Team),
            "teamColor": metadata["teamColor"],

            "stints": cls._build_stints(laps),
        }
        
    @classmethod
    def _build_stints(
        cls,
        laps: pd.DataFrame,
    ) -> list[dict[str, Any]]:

        stints = []

        for stint_number, stint_laps in laps.groupby("Stint"):

            first = stint_laps.iloc[0]
            last = stint_laps.iloc[-1]

            stints.append(
                {
                    "stint": int(stint_number),

                    "compound": cls._COMPOUNDS.normalize(
                        first.Compound
                    ),

                    "startingTyreAge": (
                        int(first.TyreLife)
                        if pd.notna(first.TyreLife)
                        else None
                    ),

                    "endingTyreAge": (
                        int(last.TyreLife)
                        if pd.notna(last.TyreLife)
                        else None
                    ),

                    "startLap": int(first.LapNumber),

                    "endLap": int(last.LapNumber),

                    "laps": [
                        cls._build_lap(lap)
                        for _, lap in stint_laps.iterrows()
                    ],
                }
            )

        return stints
        
    @classmethod
    def _build_race(
        cls,
        session,
    ) -> dict[str, Any]:

        event = session.event

        return {
            "year": int(event["EventDate"].year),
            "round": int(event["RoundNumber"]),
            "eventName": event["EventName"],
            "country": event["Country"],
            "location": event["Location"],
            "circuit": event["OfficialEventName"],
            "totalLaps": int(session.total_laps),
        }

    @classmethod
    def _build_lap(
        cls,
        lap: pd.Series,
    ) -> dict[str, Any]:

        telemetry = lap.get_car_data().add_distance()

        speeds = telemetry["Speed"]

        gear_changes = (
            telemetry["nGear"]
            .diff()
            .fillna(0)
            .ne(0)
            .sum()
        )

        return {

            "lapNumber": int(lap.LapNumber),
            
            "trackStatus": int(lap.TrackStatus),

            "lapTime": cls._format_time(lap.LapTime),

            "sector1": cls._format_time(lap.Sector1Time),

            "sector2": cls._format_time(lap.Sector2Time),

            "sector3": cls._format_time(lap.Sector3Time),

            "tyreLife": (
                int(lap.TyreLife)
                if pd.notna(lap.TyreLife)
                else None
            ),

            "position": (
                int(lap.Position)
                if pd.notna(lap.Position)
                else None
            ),

            "pitIn": pd.notna(lap.PitInTime),

            "pitOut": pd.notna(lap.PitOutTime),

            "personalBest": bool(lap.IsPersonalBest),

            "speed": {
                "top": round(float(speeds.max()), 1),
                "minimum": round(float(speeds.min()), 1),
                "average": round(float(speeds.mean()), 1),
            },

            "gearShifts": int(gear_changes),

            #
            # Phase 2
            #
            "distribution": {
                "fullThrottle": None,
                "brake": None,
                "cornering": None,
                "rolling": None,
                "liftAndCoast": None,
                "clipping": None,
            },
        }

    @staticmethod
    def _format_time(value) -> float | None:

        if pd.isna(value):
            return None

        return round(
            value.total_seconds(),
            3,
        )
        
    
    @classmethod
    def _driver_metadata(
        cls,
        session,
        driver: str,
    ) -> dict[str, Any]:

        row = (
            session.results.loc[
                session.results["Abbreviation"] == driver
            ]
            .iloc[0]
        )

        return {
            "fullName": row["FullName"],
            "headshotUrl": row["HeadshotUrl"],
            "countryCode": row["CountryCode"],
            "teamColor": row["TeamColor"],
        }