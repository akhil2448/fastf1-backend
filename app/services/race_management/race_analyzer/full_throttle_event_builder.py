from __future__ import annotations

from typing import Any


class FullThrottleEventBuilder:

    FULL_THROTTLE = {
        "FULL",
    }

    @classmethod
    def build(
        cls,
        phases: list[dict[str, Any]],
        telemetry,
        zone_progress: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        context_lookup = {
            (
                phase["startTime"],
                phase["endTime"],
            ): phase
            for phase in phases
        }

        zone_lookup = {
            (
                zone["startTime"],
                zone["endTime"],
            ): zone
            for zone in zone_progress
        }

        events = []

        current = None

        for phase in phases:

            if phase["phase"] not in cls.FULL_THROTTLE:

                if current is not None:
                    events.append(current)
                    current = None

                continue

            key = (
                phase["startTime"],
                phase["endTime"],
            )

            context = context_lookup[key]
            zone = zone_lookup[key]

            phase_object = {

                "phase": phase["phase"],

                "startTime": phase["startTime"],
                "endTime": phase["endTime"],
                "duration": phase["duration"],

                "startDistance": phase["startDistance"],
                "endDistance": phase["endDistance"],

                "previousPhase": context["previousPhase"],
                "nextPhase": context["nextPhase"],

                "previousIsBrake": context["previousIsBrake"],
                "nextIsBrake": context["nextIsBrake"],

                "previousIsThrottle": context["previousIsThrottle"],
                "nextIsThrottle": context["nextIsThrottle"],

                "zone": zone["zone"],
                "relationship": zone["relationship"],

                "entryProgress": zone["entryProgress"],
                "exitProgress": zone["exitProgress"],

                "distanceToEntry": zone["distanceToEntry"],
                "distanceToExit": zone["distanceToExit"],
            }

            if current is None:

                current = {
                    "startTime": phase["startTime"],
                    "endTime": phase["endTime"],
                    "startDistance": phase["startDistance"],
                    "endDistance": phase["endDistance"],
                    "phases": [],
                }

            elif (
                current["phases"][-1]["relationship"],
                phase_object["relationship"],
            ) in {
                ("AFTER", "BEFORE"),
                ("AFTER", "ENTERS"),
                ("AFTER", "INSIDE"),
                ("INSIDE", "AFTER"),
                ("EXITS", "BEFORE"),
            }:

                events.append(current)

                current = {
                    "startTime": phase["startTime"],
                    "endTime": phase["endTime"],
                    "startDistance": phase["startDistance"],
                    "endDistance": phase["endDistance"],
                    "phases": [],
                }

            current["phases"].append(
                phase_object
            )

            current["endTime"] = phase["endTime"]
            current["endDistance"] = phase["endDistance"]

        if current is not None:
            events.append(current)

        #
        # Lap-wide maximum speed
        #
        lap_max_speed = float(
            telemetry["Speed"].max()
        )

        #
        # Compute metrics for every event
        #
        for event in events:

            first = event["phases"][0]
            last = event["phases"][-1]

            start_phase = context_lookup[
                (
                    first["startTime"],
                    first["endTime"],
                )
            ]

            end_phase = context_lookup[
                (
                    last["startTime"],
                    last["endTime"],
                )
            ]

            start_index = start_phase["startIndex"]
            end_index = end_phase["endIndex"]

            segment = telemetry.iloc[
                start_index:end_index + 1
            ]

            start_sample = telemetry.iloc[start_index]
            end_sample = telemetry.iloc[end_index]

            event["duration"] = round(
                event["endTime"]
                - event["startTime"],
                3,
            )

            event["distance"] = round(
                event["endDistance"]
                - event["startDistance"],
                3,
            )

            event["firstRelationship"] = (
                first["relationship"]
            )

            event["lastRelationship"] = (
                last["relationship"]
            )

            event["distanceToEntry"] = (
                first["distanceToEntry"]
            )

            event["zone"] = (
                first["zone"]
            )

            #
            # Speed
            #
            event["startSpeed"] = float(
                start_sample["Speed"]
            )

            event["endSpeed"] = float(
                end_sample["Speed"]
            )

            event["speedGain"] = round(
                event["endSpeed"]
                - event["startSpeed"],
                1,
            )

            event["averageSpeed"] = round(
                float(segment["Speed"].mean()),
                1,
            )

            event["maximumSpeed"] = round(
                float(segment["Speed"].max()),
                1,
            )

            event["speedRatio"] = round(
                event["maximumSpeed"] / lap_max_speed,
                3,
            )

            event["averageAcceleration"] = round(
                event["speedGain"]
                / max(event["duration"], 0.001),
                1,
            )

            #
            # RPM
            #
            event["startRPM"] = int(
                start_sample["RPM"]
            )

            event["endRPM"] = int(
                end_sample["RPM"]
            )

            event["rpmGain"] = (
                event["endRPM"]
                - event["startRPM"]
            )

            #
            # Gear
            #
            event["startGear"] = int(
                start_sample["nGear"]
            )

            event["endGear"] = int(
                end_sample["nGear"]
            )

            #
            # DRS
            #
            event["startDRS"] = int(
                start_sample["DRS"]
            )

            event["endDRS"] = int(
                end_sample["DRS"]
            )

            #
            # Brake
            #
            event["previousIsBrake"] = (
                first["previousIsBrake"]
            )

            event["nextIsBrake"] = (
                last["nextIsBrake"]
            )

        #
        # Normalize acceleration using the strongest
        # full-throttle event of this lap.
        #
        max_acceleration = max(
            (
                max(
                    0.0,
                    event["averageAcceleration"],
                )
                for event in events
            ),
            default=0.001,
        )

        max_acceleration = max(
            max_acceleration,
            0.001,
        )

        for event in events:

            event["accelerationRatio"] = round(
                max(
                    0.0,
                    event["averageAcceleration"],
                )
                / max_acceleration,
                3,
            )

        return events