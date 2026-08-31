from __future__ import annotations

from time import perf_counter

from app.services.session_cache_service import (
    get_loaded_session,
)

from app.utils.time_utils import (
    convert_all_timedelta_columns,
)


YEAR = 2026
ROUND = 11
DRIVER = "ANT"


def main():

    session = get_loaded_session(
        YEAR,
        ROUND,
    )

    print(
        f"Loading telemetry for {DRIVER}..."
    )

    start = perf_counter()

    telemetry = (
        session.laps
        .pick_drivers([DRIVER])
        .get_telemetry()
        .copy()
    )

    telemetry = telemetry.add_distance()

    load_time = (
        perf_counter() - start
    )

    print(
        "Telemetry rows:",
        len(telemetry),
    )

    print(
        "Telemetry columns:",
        list(telemetry.columns),
    )

    print(
        "Load + add_distance:",
        f"{load_time:.6f}s",
    )

    print()

    runs = 20

    start = perf_counter()

    for _ in range(runs):

        test_df = telemetry.copy()

        convert_all_timedelta_columns(
            test_df
        )

    elapsed = (
        perf_counter() - start
    )

    print(
        "=" * 60
    )

    print(
        "TELEMETRY TIME UTILS BENCHMARK"
    )

    print(
        "=" * 60
    )

    print(
        "Rows:",
        len(telemetry),
    )

    print(
        "Runs:",
        runs,
    )

    print(
        "Total:",
        f"{elapsed:.6f}s",
    )

    print(
        "Average:",
        f"{elapsed / runs:.6f}s",
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()