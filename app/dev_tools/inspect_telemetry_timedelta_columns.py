from app.services.session_cache_service import (
    get_loaded_session,
)


YEAR = 2026
ROUND = 11
DRIVER = "ANT"


def main():

    session = get_loaded_session(
        YEAR,
        ROUND,
    )

    telemetry = (
        session.laps
        .pick_drivers([DRIVER])
        .get_telemetry()
        .copy()
    )

    telemetry = telemetry.add_distance()

    print()
    print("=" * 70)
    print("TIMEDelta COLUMNS")
    print("=" * 70)

    timedelta_columns = (
        telemetry
        .select_dtypes(
            include=["timedelta64[ns]"]
        )
        .columns
        .tolist()
    )

    print(
        "Columns:",
        timedelta_columns,
    )

    print()

    for col in timedelta_columns:

        print(
            col,
            "rows=",
            telemetry[col].notna().sum(),
            "dtype=",
            telemetry[col].dtype,
        )


if __name__ == "__main__":
    main()