from __future__ import annotations

from typing import Any


class ClippingBuilder:
    """
    Classifies full-throttle events as
    Clipping or Normal.

    The classifier uses normalized lap-relative
    metrics instead of fixed speed or acceleration
    thresholds, making it robust across different
    seasons, power units and circuits.

    This builder consumes only the evidence
    produced by FullThrottleEventBuilder.
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

        reasons = []

        #
        # Candidate 1
        # Must be near the lap's maximum speed.
        #
        if event["speedRatio"] < 0.95:

            return {
                "classification": "NORMAL",
                "score": 0,
                "reasons": reasons,
            }

        reasons.append(
            "Near lap top speed"
        )

        #
        # Candidate 2
        # Must reach top gear.
        #
        if max(
            event["startGear"],
            event["endGear"],
        ) < 7:

            return {
                "classification": "NORMAL",
                "score": 1,
                "reasons": reasons,
            }

        reasons.append(
            "Top gear"
        )

        #
        # Candidate 3
        # Must be sustained.
        #
        if event["duration"] < 0.70:

            return {
                "classification": "NORMAL",
                "score": 2,
                "reasons": reasons,
            }

        reasons.append(
            "Sustained full throttle"
        )

        #
        # Final test.
        # True clipping produces almost no
        # acceleration while remaining at
        # full throttle.
        #
        if event["accelerationRatio"] > 0.60:

            return {
                "classification": "NORMAL",
                "score": 3,
                "reasons": reasons,
            }

        reasons.append(
            "Acceleration plateau"
        )

        return {
            "classification": "CLIPPING",
            "score": 4,
            "reasons": reasons,
        }