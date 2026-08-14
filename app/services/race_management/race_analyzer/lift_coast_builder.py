from __future__ import annotations

from typing import Any


class LiftCoastBuilder:
    """
    Classifies off-throttle events as
    Lift-and-Coast or not.

    This builder consumes only the evidence
    produced by previous builders.
    """

    @classmethod
    def build(
        cls,
        events: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        results = []

        for event in events:

            classification = cls._classify(
                event,
            )

            results.append(
                {
                    **event,
                    **classification,
                }
            )

        return results

    @classmethod
    def _classify(
        cls,
        event: dict[str, Any],
    ) -> dict[str, Any]:

        score = 0

        reasons = []

        #
        # -------------------------------------------------
        # Rule 1
        #
        # A lift-and-coast event should begin before
        # entering the corner.
        # -------------------------------------------------
        #
        if (
            event["startsBeforeCorner"]
            or event["firstRelationship"] == "ENTERS"
        ):

            score += 2

            reasons.append(
                "Started before corner"
            )

        #
        # -------------------------------------------------
        # Rule 2
        #
        # Driver should not begin with throttle.
        # -------------------------------------------------
        #
        if event["previousIsThrottle"]:

            score += 1

            reasons.append(
                "Lifted from throttle"
            )

        #
        # -------------------------------------------------
        # Rule 3
        #
        # Driver should not still be braking
        # beforehand.
        # -------------------------------------------------
        #
        if not event["previousIsBrake"]:

            score += 1

            reasons.append(
                "No brake before lift"
            )

        #
        # -------------------------------------------------
        # Rule 4
        #
        # Longer events are more likely to be
        # intentional lift-and-coast.
        # -------------------------------------------------
        #
        if (
            event["duration"] >= 0.60
            or event["distance"] >= 30
        ):

            score += 1

            reasons.append(
                "Long off-throttle"
            )

        #
        # -------------------------------------------------
        # Rule 5
        #
        # Rolling is usually present.
        # -------------------------------------------------
        #
        if event["speedLoss"] >= 25:

            score += 1

            reasons.append(
                "Significant coasting"
            )
            
        #
        # -------------------------------------------------
        # Rule 6
        #
        # Large RPM drop while coasting.
        # -------------------------------------------------
        #
        if event["rpmLoss"] >= 1500:

            score += 1

            reasons.append(
                "Large RPM drop"
            )
            
        #
        # -------------------------------------------------
        # Rule 7
        #
        # Lift-and-coast usually begins on
        # a high-speed straight.
        # -------------------------------------------------
        #
        if (
            event["startSpeed"] >= 240
            or event["averageSpeed"] >= 240
        ):

            score += 1

            reasons.append(
                "High-speed coast"
            )
            
        #
        # -------------------------------------------------
        # Rule 8
        #
        # Long coasting distance before
        # braking.
        # -------------------------------------------------
        #
        if event["distance"] >= 50:

            score += 1

            reasons.append(
                "Long coasting distance"
            )
            
        #
        # Rule 9
        #
        # Event reaches the corner before braking.
        #
        if (
            event["distanceToEntry"] <= 40
            or event["firstRelationship"] in (
                "ENTERS",
                "INSIDE",
                "EXITS",
            )
        ):

            score += 1

            reasons.append(
                "Reached corner"
            )

        #
        # Final decision.
        #
        if score >= 6:

            classification = "LIFT_AND_COAST"

        else:

            classification = "ROLLING"

        return {
            "classification": classification,
            "score": score,
            "reasons": reasons,
        }