from app.services.session_cache_service import get_loaded_session
from app.services.race_management.telemetry_service import (
    TelemetryService,
)
from app.services.race_management.telemetry_cursor import (
    TelemetryCursor,
)
from app.services.race_management.telemetry_alignment import (
    TelemetryAlignment,
)


YEAR = 2026
ROUND = 2


def validate_driver(
    telemetry_service: TelemetryService,
    session,
    driver_number: str,
) -> int:

    print(
        f"\nTesting driver {driver_number}..."
    )

    frame = telemetry_service.build(
        session,
        driver_number,
    )

    samples = frame.samples

    if not samples:
        print(
            f"SKIP {driver_number}: no telemetry samples"
        )
        return 0

    cursor = TelemetryCursor(
        samples
    )

    times, indexes = (
        TelemetryAlignment.build_time_index(
            samples
        )
    )

    checked = 0

    for sample in samples:

        old_sample = cursor.nearest(
            sample.session_time
        )

        new_index = (
            TelemetryAlignment.nearest_index(
                times,
                sample.session_time,
            )
        )

        if new_index is None:
            raise AssertionError(
                f"New alignment returned None "
                f"for driver {driver_number} "
                f"at {sample.session_time}"
            )

        new_sample = samples[new_index]

        if old_sample is not new_sample:

            old_index = samples.index(
                old_sample
            )

            raise AssertionError(
                "\nTelemetry alignment mismatch\n"
                f"Driver: {driver_number}\n"
                f"Time: {sample.session_time}\n"
                f"Old index: {old_index}\n"
                f"New index: {new_index}\n"
                f"Old sample time: "
                f"{old_sample.session_time}\n"
                f"New sample time: "
                f"{new_sample.session_time}"
            )

        checked += 1

    print(
        f"PASS {driver_number}: "
        f"{checked} samples checked"
    )

    return checked


def main():

    print(
        f"Loading {YEAR} Round {ROUND}..."
    )

    session = get_loaded_session(
        YEAR,
        ROUND,
    )

    telemetry_service = (
        TelemetryService()
    )

    total_checked = 0
    drivers_tested = 0

    for driver_number in session.drivers:

        checked = validate_driver(
            telemetry_service,
            session,
            driver_number,
        )

        if checked > 0:
            drivers_tested += 1
            total_checked += checked

    print(
        "\n========================================"
    )
    print(
        "Telemetry alignment validation PASSED"
    )
    print(
        f"Drivers tested: {drivers_tested}"
    )
    print(
        f"Samples checked: {total_checked}"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":
    main()