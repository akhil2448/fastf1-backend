from __future__ import annotations

from typing import Any


class OffThrottleEventBuilder:

    OFF_THROTTLE = {
        "ROLL",
        "LIFT",
    }

    @classmethod
    def build(
        cls,
        phases: list[dict[str, Any]],
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
                z["startTime"],
                z["endTime"],
            ): z
            for z in zone_progress
        }

        events = []

        current = None

        for phase in phases:

            if phase["phase"] not in cls.OFF_THROTTLE:

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
                #
                # Driving phase
                #
                "phase": phase["phase"],

                "startTime": phase["startTime"],
                "endTime": phase["endTime"],
                "duration": phase["duration"],

                "startDistance": phase["startDistance"],
                "endDistance": phase["endDistance"],

                #
                # Context
                #
                "previousPhase": context["previousPhase"],
                "nextPhase": context["nextPhase"],

                "previousIsBrake": context["previousIsBrake"],
                "nextIsBrake": context["nextIsBrake"],

                "previousIsThrottle": context["previousIsThrottle"],
                "nextIsThrottle": context["nextIsThrottle"],

                #
                # Zone
                #
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

            current["phases"].append(
                phase_object
            )

            current["endTime"] = phase["endTime"]
            current["endDistance"] = phase["endDistance"]

        if current is not None:
            events.append(current)

        for event in events:

            event["phaseCount"] = len(
                event["phases"]
            )

            event["containsRoll"] = any(
                phase["phase"] == "ROLL"
                for phase in event["phases"]
            )

            event["containsLift"] = any(
                phase["phase"] == "LIFT"
                for phase in event["phases"]
            )

            event["startsWith"] = (
                event["phases"][0]["phase"]
            )

            event["endsWith"] = (
                event["phases"][-1]["phase"]
            )
            
            first = event["phases"][0]
            last = event["phases"][-1]

            event["firstRelationship"] = (
                first["relationship"]
            )

            event["lastRelationship"] = (
                last["relationship"]
            )

            event["entryProgress"] = (
                first["entryProgress"]
            )

            event["exitProgress"] = (
                last["exitProgress"]
            )

            event["distanceToEntry"] = (
                first["distanceToEntry"]
            )

            event["distanceToExit"] = (
                last["distanceToExit"]
            )

            event["startsBeforeCorner"] = (
                first["relationship"] == "BEFORE"
            )

            event["startsInsideCorner"] = (
                first["relationship"] == "INSIDE"
            )

            event["endsInsideCorner"] = (
                last["relationship"]
                in (
                    "INSIDE",
                    "EXITS",
                )
            )

            event["endsAfterCorner"] = (
                last["relationship"] == "AFTER"
            )

            event["zoneRelationship"] = (
                f"{first['relationship']} -> "
                f"{last['relationship']}"
            )

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
            
            event["zone"] = (
                first["zone"]
            )

        return events