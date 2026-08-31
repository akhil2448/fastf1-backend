from __future__ import annotations

from app.services.session_cache_service import (
    get_loaded_session,
)

from app.services.race_management.telemetry_service import (
    TelemetryService,
)

from app.dev_tools.telemetry_service_legacy import (
    TelemetryService as LegacyTelemetryService,
)


YEAR = 2026
ROUND = 2


def compare_frames(
    driver_number: str,
    legacy_frame,
    optimized_frame,
):
    if (
        legacy_frame.driver_number
        != optimized_frame.driver_number
    ):
        raise AssertionError(
            f"{driver_number}: driver number mismatch"
        )

    if len(legacy_frame.samples) != len(
        optimized_frame.samples
    ):
        raise AssertionError(
            f"{driver_number}: sample count mismatch: "
            f"{len(legacy_frame.samples)} != "
            f"{len(optimized_frame.samples)}"
        )

    fields = [
        "session_time",
        "lap_number",
        "distance",
        "normalized_distance",
        "speed",
        "rpm",
        "throttle",
        "brake",
        "gear",
        "drs",
    ]

    for index, (
        legacy_sample,
        optimized_sample,
    ) in enumerate(
        zip(
            legacy_frame.samples,
            optimized_frame.samples,
        )
    ):

        for field in fields:

            legacy_value = getattr(
                legacy_sample,
                field,
            )

            optimized_value = getattr(
                optimized_sample,
                field,
            )

            if legacy_value != optimized_value:

                raise AssertionError(
                    f"\nTelemetry mismatch\n"
                    f"Driver: {driver_number}\n"
                    f"Sample: {index}\n"
                    f"Field: {field}\n"
                    f"Legacy: {legacy_value!r}\n"
                    f"Optimized: {optimized_value!r}"
                )


def main():

    print(
        f"Loading {YEAR} Round {ROUND}..."
    )

    session = get_loaded_session(
        YEAR,
        ROUND,
    )

    legacy_service = (
        LegacyTelemetryService()
    )

    optimized_service = (
        TelemetryService()
    )

    drivers_tested = 0
    total_samples = 0

    print()
    print("=" * 70)
    print("TELEMETRY SERVICE VALIDATION")
    print("=" * 70)

    for driver_number in session.drivers:

        print()
        print(
            f"Testing driver: {driver_number}"
        )

        legacy_frame = (
            legacy_service.build(
                session,
                driver_number,
            )
        )

        optimized_frame = (
            optimized_service.build(
                session,
                driver_number,
            )
        )

        print(
            "Legacy samples    :",
            len(legacy_frame.samples),
        )

        print(
            "Optimized samples :",
            len(optimized_frame.samples),
        )

        compare_frames(
            driver_number,
            legacy_frame,
            optimized_frame,
        )

        print(
            f"PASS {driver_number}: "
            "telemetry output matches legacy."
        )

        drivers_tested += 1
        total_samples += len(
            optimized_frame.samples
        )

    print()
    print("=" * 70)
    print("TELEMETRY SERVICE VALIDATION PASSED")
    print("=" * 70)

    print(
        "Drivers tested:",
        drivers_tested,
    )

    print(
        "Total samples checked:",
        total_samples,
    )


if __name__ == "__main__":
    main()