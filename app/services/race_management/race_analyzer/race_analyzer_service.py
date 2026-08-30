from __future__ import annotations

from typing import Any
import logging
import time

import pandas as pd

from app.services.race_management.race_analyzer.race_metadata_builder import RaceMetadataBuilder
from app.services.race_management.race_analyzer.lap_analysis_builder import LapAnalysisBuilder
from app.services.race_management.race_analyzer.corner_zone_builder import (
    CornerZoneBuilder,
)
from app.services.team_normalizer import normalize_team_name
from app.services.race_management.tyre_compound_service import TyreCompoundService

logger = logging.getLogger(__name__)


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

        request_start = time.perf_counter()

        if not drivers:
            raise ValueError("At least one driver must be selected.")

        drivers = [d.upper() for d in drivers]

        if len(drivers) > cls.MAX_DRIVERS:
            raise ValueError("Maximum two drivers are supported.")

        reference_driver = drivers[0]

        # ----------------------------------------------------------
        # Build circuit corner zones ONCE per race-analysis request.
        # These zones are circuit/session metadata and do not depend
        # on the individual lap.
        # ----------------------------------------------------------
        corner_zone_start = time.perf_counter()

        corner_zones = CornerZoneBuilder.build(
            session,
        )

        logger.info(
            "[RACE ANALYZER PERF] corner_zones=%.3fs count=%d",
            time.perf_counter() - corner_zone_start,
            len(corner_zones),
        )

        race_start = time.perf_counter()

        race = cls._build_race(session)

        logger.info(
            "[RACE ANALYZER PERF] race_build=%.3fs",
            time.perf_counter() - race_start,
        )

        metadata_start = time.perf_counter()

        track_metadata = RaceMetadataBuilder.build(
            session=session,
            reference_driver=reference_driver,
        )

        logger.info(
            "[RACE ANALYZER PERF] track_metadata=%.3fs",
            time.perf_counter() - metadata_start,
        )

        driver_results = []

        for driver in drivers:

            driver_start = time.perf_counter()

            result = cls._build_driver(
                session=session,
                driver=driver,
                corner_zones=corner_zones,
            )

            driver_results.append(result)

            logger.info(
                "[RACE ANALYZER PERF] driver=%s time=%.3fs",
                driver,
                time.perf_counter() - driver_start,
            )

        total_time = time.perf_counter() - request_start

        logger.info(
            "[RACE ANALYZER PERF] total=%.3fs drivers=%s",
            total_time,
            ",".join(drivers),
        )

        return {
            "race": race,

            "referenceDriver": reference_driver,

            "trackMetadata": track_metadata,

            "drivers": driver_results,
        }

    @classmethod
    def _build_driver(
        cls,
        session,
        driver: str,
        corner_zones: list[dict[str, Any]],
    ) -> dict[str, Any]:

        laps = session.laps.pick_drivers(driver)

        if laps.empty:
            raise ValueError(f"No laps found for driver '{driver}'")

        info = laps.iloc[0]
        
        metadata = cls._driver_metadata(session, driver)

        valid_laps = laps.dropna(
            subset=["LapTime"]
        )

        personal_best_time = (
            valid_laps["LapTime"].min()
            if not valid_laps.empty
            else None
        )

        return {
            "driver": driver,
            "driverNumber": str(info.DriverNumber),

            "fullName": metadata["fullName"],
            "headshotUrl": metadata["headshotUrl"],
            "countryCode": metadata["countryCode"],

            "teamName": normalize_team_name(info.Team),
            "teamColor": metadata["teamColor"],

            "stints": cls._build_stints(
                laps,
                personal_best_time,
                corner_zones,
            ),
        }
        
    @classmethod
    def _build_stints(
        cls,
        laps: pd.DataFrame,
        personal_best_time,
        corner_zones: list[dict[str, Any]],
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
                        cls._build_lap(
                            lap,
                            personal_best_time,
                            corner_zones,
                        )
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

        valid_laps = session.laps.dropna(
            subset=["LapTime"]
        )

        fastest_lap = (
            valid_laps.loc[
                valid_laps["LapTime"].idxmin()
            ]
            if not valid_laps.empty
            else None
        )

        return {
            "year": int(event["EventDate"].year),
            "round": int(event["RoundNumber"]),
            "eventName": event["EventName"],
            "country": event["Country"],
            "location": event["Location"],
            "circuit": event["OfficialEventName"],
            "totalLaps": int(session.total_laps),

            "sessionFastest": (
                round(
                    fastest_lap["LapTime"].total_seconds(),
                    3,
                )
                if fastest_lap is not None
                else None
            ),

            "sessionFastestDriver": (
                str(fastest_lap["Driver"])
                if fastest_lap is not None
                else None
            ),

            "sessionFastestLap": (
                int(fastest_lap["LapNumber"])
                if fastest_lap is not None
                else None
            ),
        }

    @classmethod
    def _build_lap(
        cls,
        lap: pd.Series,
        personal_best_time,
        corner_zones: list[dict[str, Any]],
    ) -> dict[str, Any]:

        telemetry = lap.get_car_data().add_distance()

        analysis = LapAnalysisBuilder.build(
            telemetry=telemetry,
            corner_zones=corner_zones,
        )

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

            "personalBest": (
                pd.notna(lap.LapTime)
                and personal_best_time is not None
                and lap.LapTime == personal_best_time
            ),

            "speed": {
                "top": round(float(speeds.max()), 1),
                "minimum": round(float(speeds.min()), 1),
                "average": round(float(speeds.mean()), 1),
            },

            "gearShifts": int(gear_changes),

            #
            # Phase 2
            #
            "distribution": analysis["distribution"],
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