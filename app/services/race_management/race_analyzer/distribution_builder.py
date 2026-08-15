from __future__ import annotations


class DistributionBuilder:
    """
    Builds the driver's throttle/braking distribution
    from the classified driving phases.
    """

    @classmethod
    def build(
        cls,
        phases: list[dict],
        corner_time: dict,
        classified_events: list[dict],
        clipping_events,
    ) -> dict:

        if not phases:
            return cls._empty_distribution()

        total_time = phases[-1]["endTime"] - phases[0]["startTime"]

        if total_time <= 0:
            return cls._empty_distribution()

        times = {
            "FULL": 0.0,
            "BRAKE": 0.0,
            "PART": 0.0,
        }

        #
        # Sum time spent in each phase.
        #
        for phase in phases:

            phase_name = phase["phase"]

            if phase_name not in times:
                continue

            times[phase_name] += phase["duration"]
            
        
        rolling_time = 0.0
        lift_coast_time = 0.0

        for event in classified_events:

            if event["classification"] == "ROLLING":

                rolling_time += event["duration"]

            elif event["classification"] == "LIFT_AND_COAST":

                lift_coast_time += event["duration"]
                
        
        clipping_time = 0.0

        for event in clipping_events:

            if event["classification"] != "CLIPPING":
                continue

            clipping_time += event["clippingDuration"]

        return {
            "fullThrottle": round(
                times["FULL"] / total_time * 100,
                2,
            ),
            "brake": round(
                times["BRAKE"] / total_time * 100,
                2,
            ),
           "rolling": round(
                rolling_time / total_time * 100,
                2,
            ),
            "partialThrottle": round(
                times["PART"] / total_time * 100,
                2,
            ),
            "liftAndCoast": round(
                lift_coast_time / total_time * 100,
                2,
            ),
            "cornering": corner_time["cornerPercentage"],
            "clipping": round(
                clipping_time / total_time * 100,
                2,
            ),
        }

    @classmethod
    def _empty_distribution(
        cls,
    ) -> dict:

        return {
            "fullThrottle": 0.0,
            "brake": 0.0,
            "rolling": 0.0,
            "partialThrottle": 0.0,
            "liftAndCoast": 0.0,
            "cornering": 0.0,
            "clipping": 0.0,
        }
        