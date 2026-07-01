import fastf1

from app.services.race_management.stint_analyzer import StintAnalyzer

YEAR = 2024
ROUND = 11
DRIVER = "HAM"


def main():

    fastf1.Cache.enable_cache("cache")

    session = fastf1.get_session(YEAR, ROUND, "R")

    session.load(
        laps=True,
        telemetry=False,
        weather=False,
        messages=False,
    )

    laps = session.laps.pick_drivers(DRIVER)

    analyzer = StintAnalyzer()

    stints = analyzer.analyze(laps)

    print()

    for stint in stints:

        print("=" * 90)

        print(f"Stint      : {stint.stint}")
        print(f"Compound   : {stint.compound}")
        print(f"Laps       : {stint.start_lap}-{stint.end_lap}")
        print(f"Tyre Life  : {stint.tyre_life_start}-{stint.tyre_life_end}")

        print()

        for lap in stint.analyzed_laps:

            status = "VALID" if lap.analysis.valid else "INVALID"

            print(
                f"Lap {lap.lap_number:>2} | "
                f"Age {lap.tyre_life:>2} | "
                f"P{lap.position:>2} | "
                f"{status}"
            )

            if not lap.analysis.valid:

                for reason in lap.analysis.reasons:

                    print(f"        - {reason}")

        print()


if __name__ == "__main__":
    main()