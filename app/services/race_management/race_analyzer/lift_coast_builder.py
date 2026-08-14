from __future__ import annotations

from typing import Any


class LiftCoastBuilder:
    """
    Classifies off-throttle events as
    Lift-and-Coast or Rolling.

    All decision thresholds are expressed as
    lap-relative normalized metrics rather than
    absolute telemetry values. This keeps the
    classifier portable across seasons, engines,
    and circuit characteristics.

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
        # Candidate filter
        #
        # Lift-and-coast should not begin after
        # the corner has already been completed.
        # -------------------------------------------------
        #
        if event["firstRelationship"] == "AFTER":

            return {
                "classification": "ROLLING",
                "score": 0,
                "reasons": reasons,
            }
        
        #
        # -------------------------------------------------
        # Candidate filter
        #
        # Ignore very low-speed off-throttle events.
        # They are normal transitions rather than
        # meaningful rolling or lift-and-coast.
        # -------------------------------------------------
        #
        if event["speedRatio"] < 0.50:

            return {
                "classification": "ROLLING",
                "score": 0,
                "reasons": reasons,
            }
            
        
        #
        # Ignore tiny off-throttle lifts.
        #
        if (
            event["durationRatio"] < 0.30
            and event["distanceRatio"] < 0.40
        ):

            return {
                "classification": "ROLLING",
                "score": 0,
                "reasons": reasons,
            }

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
            event["durationRatio"] >= 0.35
            or event["distanceRatio"] >= 0.35
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
        if event["speedLossRatio"] >= 0.35:

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
        if event["rpmLossRatio"] >= 0.45:

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
        if event["speedRatio"] >= 0.90:

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
        if event["distanceRatio"] >= 0.40:

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
        if score >= 7:

            classification = "LIFT_AND_COAST"

        else:

            classification = "ROLLING"

        return {
            "classification": classification,
            "score": score,
            "reasons": reasons,
        }