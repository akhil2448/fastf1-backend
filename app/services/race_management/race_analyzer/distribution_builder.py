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
    ) -> dict:

        if not phases:
            return cls._empty_distribution()

        total_time = phases[-1]["endTime"] - phases[0]["startTime"]

        if total_time <= 0:
            return cls._empty_distribution()

        times = {
            "FULL": 0.0,
            "BRAKE": 0.0,
            "ROLL": 0.0,
            "LIFT": 0.0,
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
                times["ROLL"] / total_time * 100,
                2,
            ),
            "partialThrottle": round(
                times["PART"] / total_time * 100,
                2,
            ),
            "lift": round(
                times["LIFT"] / total_time * 100,
                2,
            ),
            "cornering": corner_time["cornerPercentage"],
            "clipping": 0.0,
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
            "lift": 0.0,
            "cornering": 0.0,
            "clipping": 0.0,
        }
        