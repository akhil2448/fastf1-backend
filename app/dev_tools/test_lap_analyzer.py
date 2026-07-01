import fastf1

from app.services.race_management.lap_analyzer import LapAnalyzer

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

    analyzer = LapAnalyzer()

    laps = session.laps.pick_drivers(DRIVER)

    print()

    for _, lap in laps.iterrows():

        result = analyzer.analyze(lap)

        lap_number = int(lap["LapNumber"])

        if result.valid:
            print(f"Lap {lap_number:>2}  ✅ VALID")

        else:
            print(f"Lap {lap_number:>2}  ❌ INVALID")

            for reason in result.reasons:
                print(f"      - {reason}")

        print()


if __name__ == "__main__":
    main()