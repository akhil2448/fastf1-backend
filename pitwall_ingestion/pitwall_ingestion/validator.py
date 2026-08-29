from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from .requirements import required_files


@dataclass
class ValidationResult:
    complete: bool
    status: str
    path: str
    size_bytes: int
    files: list[str]
    missing_files: list[str]
    zero_byte_files: list[str]
    logical_checks: dict[str, Any]
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def directory_size(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def filesystem_validate(session_dir: Path, session_type: str) -> ValidationResult:
    """Audit the native FastF1 files written for this session."""
    if not session_dir.exists():
        return ValidationResult(
            complete=False,
            status="missing",
            path=str(session_dir),
            size_bytes=0,
            files=[],
            missing_files=sorted(required_files(session_type)),
            zero_byte_files=[],
            logical_checks={},
            errors=["Session directory does not exist"],
        )

    files = sorted(p.name for p in session_dir.iterdir() if p.is_file())
    sizes = {p.name: p.stat().st_size for p in session_dir.iterdir() if p.is_file()}
    required = required_files(session_type)
    missing = sorted(required - set(files))
    zero_bytes = sorted(name for name, size in sizes.items() if size == 0)

    complete = not missing and not zero_bytes
    return ValidationResult(
        complete=complete,
        status="complete" if complete else "incomplete",
        path=str(session_dir),
        size_bytes=directory_size(session_dir),
        files=files,
        missing_files=missing,
        zero_byte_files=zero_bytes,
        logical_checks={},
        errors=[],
    )


def _record_check(label: str, fn, checks: dict[str, Any], errors: list[str]) -> None:
    try:
        value = bool(fn())
        checks[label] = value
        if not value:
            errors.append(f"Logical check failed: {label}")
    except Exception as exc:
        checks[label] = False
        errors.append(f"Logical check error ({label}): {type(exc).__name__}: {exc}")


def logical_validate(session, session_type: str) -> ValidationResult:
    """Verify the session properties that PitWall actually consumes."""
    checks: dict[str, Any] = {}
    errors: list[str] = []

    _record_check("laps_nonempty", lambda: len(session.laps) > 0, checks, errors)
    _record_check("results_nonempty", lambda: len(session.results) > 0, checks, errors)
    _record_check("drivers_nonempty", lambda: len(session.drivers) > 0, checks, errors)
    _record_check(
        "circuit_info_available",
        lambda: session.get_circuit_info() is not None,
        checks,
        errors,
    )

    def fastest_lap_telemetry_ok() -> bool:
        lap = session.laps.pick_fastest()
        if lap is None:
            return False
        telemetry = lap.get_telemetry()
        return (
            not telemetry.empty
            and {"X", "Y", "Distance"}.issubset(telemetry.columns)
        )

    _record_check("fastest_lap_xy_distance_telemetry", fastest_lap_telemetry_ok, checks, errors)

    def car_data_ok() -> bool:
        value = session.car_data
        return value is not None and len(value) > 0

    def position_data_ok() -> bool:
        value = session.pos_data
        return value is not None and len(value) > 0

    _record_check("car_data_available", car_data_ok, checks, errors)
    _record_check("position_data_available", position_data_ok, checks, errors)

    if session_type == "R":
        _record_check(
            "weather_available",
            lambda: session.weather_data is not None and len(session.weather_data) > 0,
            checks,
            errors,
        )
        _record_check(
            "race_control_available",
            lambda: session.race_control_messages is not None,
            checks,
            errors,
        )
        _record_check(
            "total_laps_available",
            lambda: session.total_laps is not None and int(session.total_laps) > 0,
            checks,
            errors,
        )

    return ValidationResult(
        complete=not errors,
        status="complete" if not errors else "invalid",
        path="",
        size_bytes=0,
        files=[],
        missing_files=[],
        zero_byte_files=[],
        logical_checks=checks,
        errors=errors,
    )


def final_status(filesystem: ValidationResult, logical: ValidationResult) -> tuple[str, list[str]]:
    """Combine native-file and logical checks into the historical archive status."""
    errors = list(filesystem.errors)
    errors.extend(filesystem.missing_files)
    errors.extend(filesystem.zero_byte_files)
    errors.extend(logical.errors)

    if filesystem.complete and logical.complete:
        return "complete", errors
    return "failed", errors
