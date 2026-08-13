from __future__ import annotations

from copy import deepcopy
from typing import Any


class PhaseContextBuilder:
    """
    Adds contextual information to driving phases.

    This builder does not inspect telemetry.
    It only relates each phase to its neighbouring
    phases and groups continuous off-throttle events.
    """

    OFF_THROTTLE = {
        "ROLL",
        "LIFT",
    }

    THROTTLE = {
        "FULL",
        "PART",
    }

    @classmethod
    def build(
        cls,
        phases: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        if not phases:
            return []

        results = []

        event_id = 0
        previous_off_throttle = False

        for index, phase in enumerate(phases):

            phase = deepcopy(phase)

            previous = (
                phases[index - 1]
                if index > 0
                else None
            )

            next_phase = (
                phases[index + 1]
                if index < len(phases) - 1
                else None
            )

            #
            # Build off-throttle event ids.
            #
            if phase["phase"] in cls.OFF_THROTTLE:

                if not previous_off_throttle:
                    event_id += 1

                phase["offThrottleEventId"] = event_id
                previous_off_throttle = True

            else:

                phase["offThrottleEventId"] = None
                previous_off_throttle = False

            phase["previousPhase"] = (
                None
                if previous is None
                else previous["phase"]
            )

            phase["nextPhase"] = (
                None
                if next_phase is None
                else next_phase["phase"]
            )

            phase["previousDuration"] = (
                None
                if previous is None
                else previous["duration"]
            )

            phase["nextDuration"] = (
                None
                if next_phase is None
                else next_phase["duration"]
            )

            phase["previousDistance"] = (
                None
                if previous is None
                else previous["distance"]
            )

            phase["nextDistance"] = (
                None
                if next_phase is None
                else next_phase["distance"]
            )

            phase["previousIsBrake"] = (
                previous is not None
                and previous["phase"] == "BRAKE"
            )

            phase["nextIsBrake"] = (
                next_phase is not None
                and next_phase["phase"] == "BRAKE"
            )

            phase["previousIsThrottle"] = (
                previous is not None
                and previous["phase"] in cls.THROTTLE
            )

            phase["nextIsThrottle"] = (
                next_phase is not None
                and next_phase["phase"] in cls.THROTTLE
            )

            results.append(phase)

        return results