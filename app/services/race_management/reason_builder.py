class ReasonBuilder:

    """
    Converts the outputs of all analyzers into a single
    human-readable explanation list.

    This class contains presentation logic only.

    It should never calculate scores or perform analysis.
    """

    ##############################################################

    def build(
        self,
        lap,
        lap_time,
        sector,
        position,
        traffic,
    ) -> list[str]:

        reasons = []

        ##########################################################
        # Lap validity reasons
        ##########################################################

        reasons.extend(
            lap.analysis.reasons
        )

        ##########################################################
        # Lap Time
        ##########################################################

        delta = lap_time.delta_seconds

        if abs(delta) <= 0.10:

            reasons.append(
                "Lap time matched the stint median"
            )

        elif delta < 0:

            reasons.append(
                f"Lap was {-delta:.3f}s faster than expected"
            )

        else:

            reasons.append(
                f"Lap was {delta:.3f}s slower than expected"
            )

        ##########################################################
        # Sector consistency
        ##########################################################

        sector_deltas = {

            "Sector 1": abs(sector.delta_sector1),

            "Sector 2": abs(sector.delta_sector2),

            "Sector 3": abs(sector.delta_sector3),
        }

        worst_sector = max(
            sector_deltas,
            key=sector_deltas.get,
        )

        largest_delta = sector_deltas[
            worst_sector
        ]

        if largest_delta <= 0.05:

            reasons.append(
                "All three sectors were consistent"
            )

        else:

            reasons.append(
                f"Largest time loss occurred in {worst_sector}"
            )

        ##########################################################
        # Position stability
        ##########################################################

        delta_position = abs(
            position.delta_position
        )

        if delta_position == 0:

            reasons.append(
                "Position remained stable"
            )

        elif delta_position == 1:

            reasons.append(
                "Position changed by one place"
            )

        else:

            reasons.append(
                f"Position changed by {int(delta_position)} places"
            )

        ##########################################################
        # Traffic
        ##########################################################

        reasons.extend(
            traffic.reasons
        )

        ##########################################################
        # Wake summary
        ##########################################################

        if traffic.wake:

            wake = traffic.wake

            reasons.append(
                f"Wake profile: {wake.profile}"
            )

            if wake.drs_factor < 1.0:

                reasons.append(
                    "DRS reduced aerodynamic wake"
                )

        ##########################################################

        return reasons