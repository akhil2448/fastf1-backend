from app.services.session_cache_service import (
    get_loaded_session,
)

YEAR = 2024
ROUND = 11


def main():

    session = get_loaded_session(

        YEAR,
        ROUND,

    )

    print()
    print("=" * 100)
    print("SESSION.RESULTS")
    print("=" * 100)
    print()

    print(session.results.columns.tolist())

    print()

    print(
        session.results[
            [
                "Position",
                "GridPosition",
                "DriverNumber",
                "Abbreviation",
                "FullName",
                "TeamName",
                "TeamColor",
                "Laps",
                "Status",
            ]
        ]
    )

    ##############################################################

    print()
    print("=" * 100)
    print("SESSION.LAPS")
    print("=" * 100)
    print()

    print(session.laps.columns.tolist())

    ##############################################################

    driver = session.results.iloc[0]["DriverNumber"]

    laps = session.laps.pick_drivers(driver)

    print()
    print("=" * 100)
    print(f"DRIVER {driver}")
    print("=" * 100)
    print()

    print(

        laps[
            [
                "LapNumber",
                "Stint",
                "Compound",
                "TyreLife",
                "PitOutTime",
                "PitInTime",
                "FreshTyre",
            ]
        ]

    )

    ##############################################################

    print()
    print("=" * 100)
    print("STINT SUMMARY")
    print("=" * 100)
    print()

    for stint, stint_df in laps.groupby("Stint"):

        print(

            f"Stint {int(stint)}"

            f" | {stint_df.iloc[0]['Compound']}"

            f" | Laps "

            f"{int(stint_df['LapNumber'].min())}"

            f"-{int(stint_df['LapNumber'].max())}"

            f" ({len(stint_df)})"

        )


if __name__ == "__main__":

    main()