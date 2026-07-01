from collections import Counter

import fastf1

from app.services.session_cache_service import get_loaded_session

START_YEAR = 2018
END_YEAR = 2025


def main():

    fastf1.Cache.enable_cache("cache")

    compound_lap_counts = Counter()
    compound_examples = {}

    total_races = 0
    skipped_races = 0

    for year in range(START_YEAR, END_YEAR + 1):

        print(f"\n========== {year} ==========")

        try:
            schedule = fastf1.get_event_schedule(year)
        except Exception as e:
            print(f"Unable to load schedule: {e}")
            continue

        races = schedule[schedule["RoundNumber"] > 0]

        for _, event in races.iterrows():

            round_number = int(event["RoundNumber"])
            race_name = event["EventName"]

            total_races += 1

            print(f"Loading {year} Round {round_number} - {race_name}")

            try:

                session = get_loaded_session(
                    year,
                    round_number
                )

            except Exception as e:

                skipped_races += 1
                print(f"  Failed to load session: {e}")
                continue

            # Some historical sessions don't have laps loaded correctly.
            try:
                laps = session.laps

            except Exception as e:

                skipped_races += 1
                print(f"  Skipping (laps unavailable): {e}")
                continue

            if laps is None or laps.empty:
                skipped_races += 1
                print("  Skipping (no lap data)")
                continue

            compound_counts = (
                laps["Compound"]
                .dropna()
                .astype(str)
                .str.upper()
                .value_counts()
            )

            for compound, lap_count in compound_counts.items():

                compound_lap_counts[compound] += int(lap_count)

                if compound not in compound_examples:

                    compound_examples[compound] = (
                        year,
                        round_number,
                        race_name,
                    )

    print("\n")
    print("=" * 90)
    print("UNIQUE TYRE COMPOUNDS")
    print("=" * 90)

    for compound in sorted(compound_lap_counts):

        year, rnd, race = compound_examples[compound]

        print(
            f"{compound:<18}"
            f"{compound_lap_counts[compound]:>8} laps"
            f"    First Seen: {year} R{rnd} ({race})"
        )

    print("\n")
    print("=" * 90)
    print(f"Total races scanned : {total_races}")
    print(f"Skipped races       : {skipped_races}")
    print("=" * 90)


if __name__ == "__main__":
    main()