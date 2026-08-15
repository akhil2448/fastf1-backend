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
    def _detect_clipping_window(
        cls,
        event: dict[str, Any],
    ) -> dict[str, Any]:

        speeds = event["speedSamples"]
        gears = event["gearSamples"]
        times = event["timeSamples"]
        distances = event["distanceSamples"]

        if len(speeds) < 4:

            return {
                "startIndex": None,
                "endIndex": None,
                "duration": 0.0,
                "distance": 0.0,
            }

        max_speed = max(speeds)

        speed_threshold = (
            max_speed * 0.98
        )

        start = None

        #
        # Look for the first point where:
        #
        # - speed is near maximum
        # - already in high gear
        # - speed has stopped increasing
        #
        for i in range(2, len(speeds) - 2):

            if gears[i] < 7:
                continue

            if speeds[i] < speed_threshold:
                continue

            delta1 = abs(
                speeds[i] - speeds[i - 1]
            )

            delta2 = abs(
                speeds[i + 1] - speeds[i]
            )

            delta3 = abs(
                speeds[i + 2] - speeds[i + 1]
            )

            if (
                delta1 <= 0.5
                and delta2 <= 0.5
                and delta3 <= 0.5
            ):

                start = i
                break

        if start is None:

            return {
                "startIndex": None,
                "endIndex": None,
                "duration": 0.0,
                "distance": 0.0,
            }

        end = start

        for i in range(start + 1, len(speeds)):

            #
            # Clipping ends if the driver
            # leaves top gear.
            #
            if gears[i] < 7:
                break

            #
            # Clipping ends if speed starts
            # dropping noticeably.
            #
            if speeds[i] < speed_threshold:
                break

            #
            # Clipping ends once the car
            # begins accelerating again.
            #
            if i < len(speeds) - 1:

                delta = speeds[i + 1] - speeds[i]

                if delta > 1.0:
                    break

            end = i
            
        
        #
        # Ignore extremely small plateaus.
        #
        if end <= start:

            return {
                "startIndex": None,
                "endIndex": None,
                "duration": 0.0,
                "distance": 0.0,
            }

        return {

            "startIndex": start,

            "endIndex": end,

            "duration": round(
                times[end] - times[start],
                3,
            ),

            "distance": round(
                distances[end]
                - distances[start],
                1,
            ),
        }

    @classmethod
    def _classify(
        cls,
        event: dict[str, Any],
    ) -> dict[str, Any]:

        reasons = []
        
        clipping_window = (
            cls._detect_clipping_window(
                event,
            )
        )

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
        #
        if clipping_window["duration"] == 0.0:

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

            "clippingStartIndex": clipping_window["startIndex"],
            "clippingEndIndex": clipping_window["endIndex"],
            "clippingDuration": clipping_window["duration"],
            "clippingDistance": clipping_window["distance"],
        }