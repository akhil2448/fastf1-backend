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
    ) -> dict:

        if not phases:
            return cls._empty_distribution()

        total_distance = phases[-1]["endDistance"]

        if total_distance <= 0:
            return cls._empty_distribution()

        distances = {
            "FULL": 0.0,
            "BRAKE": 0.0,
            "ROLL": 0.0,
            "LIFT": 0.0,
            "PART": 0.0,
        }

        #
        # Sum distance travelled in each phase.
        #
        for phase in phases:

            phase_name = phase["phase"]

            if phase_name not in distances:
                continue

            distances[phase_name] += phase["distance"]

        return {
            "fullThrottle": round(
                distances["FULL"] / total_distance * 100,
                2,
            ),
            "brake": round(
                distances["BRAKE"] / total_distance * 100,
                2,
            ),
            "rolling": round(
                distances["ROLL"] / total_distance * 100,
                2,
            ),
            "partialThrottle": round(
                distances["PART"] / total_distance * 100,
                2,
            ),
            "lift": round(
                distances["LIFT"] / total_distance * 100,
                2,
            ),
            "cornering": cls._build_cornering(
                phases,
                total_distance,
            ),
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
        
    
    @classmethod
    def _build_cornering(
        cls,
        phases: list[dict],
        total_distance: float,
    ) -> float:

        if total_distance <= 0:
            return 0.0

        corner_distance = 0.0

        in_corner = False

        for phase in phases:

            phase_name = phase["phase"]

            #
            # Corner starts when braking begins.
            #
            if phase_name == "BRAKE":
                in_corner = True

            #
            # Everything after braking is considered
            # part of the corner until full throttle.
            #
            if in_corner:
                corner_distance += phase["distance"]

            #
            # Corner ends once full throttle resumes.
            #
            if phase_name == "FULL":
                in_corner = False

        return round(
            corner_distance / total_distance * 100,
            2,
        )