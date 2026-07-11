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

            "Sector 1": sector.delta_sector1,

            "Sector 2": sector.delta_sector2,

            "Sector 3": sector.delta_sector3,
        }

        worst_sector = max(

            sector_deltas,

            key=lambda sector_name: abs(

                sector_deltas[sector_name]

            ),

        )

        largest_delta = sector_deltas[
            worst_sector
        ]

        if abs(largest_delta) <= 0.05:

            reasons.append(
                "All three sectors were consistent"
            )

        else:

            reasons.append(

                f"Largest sector deviation: "

                f"{worst_sector} "

                f"({largest_delta:+.3f}s)"

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
        # Tyres
        ##########################################################

        reasons.append(

            f"{lap.compound} tyres with "
            f"{lap.tyre_life} lap"

            f"{'' if lap.tyre_life == 1 else 's'} of wear"

        )

        ##########################################################
        # Traffic / Wake
        ##########################################################

        clean = traffic.clean_air_percentage
        wake = traffic.average_wake_strength * 100

        if clean >= 95:

            reasons.append(

                f"Ran in clean air with "
                f"minimal wake ({wake:.0f}%)"

            )

        elif clean >= 75:

            reasons.append(

                f"Mostly clean air with "
                f"light wake ({wake:.0f}%)"

            )

        elif clean >= 50:

            reasons.append(

                f"Light traffic with "
                f"moderate wake ({wake:.0f}%)"

            )

        elif clean >= 25:

            reasons.append(

                f"Moderate traffic with "
                f"noticeable wake ({wake:.0f}%)"

            )

        else:

            reasons.append(

                f"Heavy traffic with "
                f"significant wake ({wake:.0f}%)"

            )

        ##########################################################

        return reasons