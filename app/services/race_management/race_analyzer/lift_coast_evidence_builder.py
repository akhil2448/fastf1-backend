from __future__ import annotations

from typing import Any


class LiftCoastEvidenceBuilder:
    """
    Builds timing statistics for all off-throttle phases.

    No classification is performed yet.
    This builder simply exposes every ROLL/LIFT phase
    together with enough context to derive lift-and-coast
    detection rules.
    """

    OFF_THROTTLE_PHASES = {
        "ROLL",
        "LIFT",
    }

    @classmethod
    def build(
        cls,
        phases: list[dict[str, Any]],
        telemetry,
        corner_zones: list[dict[str, Any]],
        zone_progress: list[dict[str, Any]],
    ) -> dict[str, Any]:

        if not phases:
            return {
                "lapTime": 0.0,
                "offThrottleTime": 0.0,
                "percentage": 0.0,
                "segments": [],
            }

        lap_time = (
            phases[-1]["endTime"]
            - phases[0]["startTime"]
        )

        total_time = 0.0

        segments = []

        for index, phase in enumerate(phases):

            if phase["phase"] not in cls.OFF_THROTTLE_PHASES:
                continue

            duration = phase["duration"]

            total_time += duration
            
            start_sample = telemetry.iloc[
                phase["startIndex"]
            ]

            end_sample = telemetry.iloc[
                phase["endIndex"]
            ]
            
            segment = telemetry.iloc[
                phase["startIndex"] :
                phase["endIndex"] + 1
            ]

            average_speed = float(
                segment["Speed"].mean()
            )

            minimum_speed = float(
                segment["Speed"].min()
            )

            maximum_speed = float(
                segment["Speed"].max()
            )

            corner_zone = cls._find_corner_zone(
                phase,
                corner_zones,
            )
            
            zone_result = next(
                (
                    result
                    for result in zone_progress
                    if (
                        result["startTime"] == phase["startTime"]
                        and result["endTime"] == phase["endTime"]
                    )
                ),
                None,
            )

            segments.append(
                {
                    "phase": phase["phase"],

                    "previousPhase": phase["previousPhase"],
                    "nextPhase": phase["nextPhase"],

                    "previousIsBrake": phase["previousIsBrake"],
                    "nextIsBrake": phase["nextIsBrake"],

                    "previousIsThrottle": phase["previousIsThrottle"],
                    "nextIsThrottle": phase["nextIsThrottle"],

                    "offThrottleEventId": phase["offThrottleEventId"],

                    "startTime": phase["startTime"],
                    "endTime": phase["endTime"],
                    "duration": duration,

                    "startDistance": phase["startDistance"],
                    "endDistance": phase["endDistance"],

                    #
                    # Raw telemetry at phase boundaries.
                    #
                    "startSpeed": float(start_sample["Speed"]),
                    "endSpeed": float(end_sample["Speed"]),

                    "averageSpeed": round(
                        average_speed,
                        1,
                    ),

                    "minimumSpeed": round(
                        minimum_speed,
                        1,
                    ),

                    "maximumSpeed": round(
                        maximum_speed,
                        1,
                    ),
                    
                    "speedChange": round(
                        float(end_sample["Speed"])
                        - float(start_sample["Speed"]),
                        1,
                    ),

                    "startThrottle": float(start_sample["Throttle"]),
                    "endThrottle": float(end_sample["Throttle"]),
                    "throttleChange": round(
                        float(end_sample["Throttle"])
                        - float(start_sample["Throttle"]),
                        1,
                    ),

                    "startBrake": bool(start_sample["Brake"]),
                    "endBrake": bool(end_sample["Brake"]),

                    "startGear": int(start_sample["nGear"]),
                    "endGear": int(end_sample["nGear"]),
                    "gearChange": (
                        int(end_sample["nGear"])
                        - int(start_sample["nGear"])
                    ),

                    "startRPM": int(start_sample["RPM"]),
                    "endRPM": int(end_sample["RPM"]),
                    "rpmChange": (
                        int(end_sample["RPM"])
                        - int(start_sample["RPM"])
                    ),

                    "startDRS": int(start_sample["DRS"]),
                    "endDRS": int(end_sample["DRS"]),
                    
                    "cornerZone": corner_zone,

                    "relationship": (
                        zone_result["relationship"]
                        if zone_result
                        else None
                    ),

                    "entryProgress": (
                        zone_result["entryProgress"]
                        if zone_result
                        else None
                    ),

                    "exitProgress": (
                        zone_result["exitProgress"]
                        if zone_result
                        else None
                    ),

                    "distanceToEntry": (
                        zone_result["distanceToEntry"]
                        if zone_result
                        else None
                    ),

                    "distanceToExit": (
                        zone_result["distanceToExit"]
                        if zone_result
                        else None
                    ),
                }
            )

        return {
            "lapTime": round(
                lap_time,
                3,
            ),
            "offThrottleTime": round(
                total_time,
                3,
            ),
            "percentage": round(
                total_time / lap_time * 100,
                2,
            ) if lap_time > 0 else 0.0,
            "segments": segments,
        }
    
    @classmethod
    def _find_corner_zone(
        cls,
        phase: dict[str, Any],
        corner_zones: list[dict[str, Any]],
    ):

        segment_start = phase["startDistance"]
        segment_end = phase["endDistance"]

        for zone in corner_zones:

            #
            # Segment overlaps this corner zone.
            #
            if (
                segment_end >= zone["startDistance"]
                and segment_start <= zone["endDistance"]
            ):
                return zone

        return None