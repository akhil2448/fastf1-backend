from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    return float(value)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CACHE_DIR = PROJECT_ROOT / "cache"
DEFAULT_METADATA_DIR = PROJECT_ROOT / ".pitwall-ingestion"


@dataclass(frozen=True)
class IngestionConfig:
    # Resolve the repository cache independently of the current working directory.
    # Override with FASTF1_CACHE_DIR when intentionally using another cache.
    cache_dir: Path = Path(os.getenv("FASTF1_CACHE_DIR", str(DEFAULT_CACHE_DIR))).expanduser().resolve()
    metadata_dir: Path = Path(
        os.getenv("PITWALL_INGESTION_METADATA_DIR", str(DEFAULT_METADATA_DIR))
    ).expanduser().resolve()

    start_year: int = _env_int("PITWALL_START_YEAR", 2018)
    current_year: int = _env_int("PITWALL_CURRENT_YEAR", 2026)

    # Additional delay between completed session loads. FastF1's own
    # request-level limiter remains untouched and continues to control the
    # individual upstream requests inside session.load().
    session_cooldown_seconds: float = _env_float(
        "PITWALL_SESSION_COOLDOWN_SECONDS", 120.0
    )

    # How many sessions one invocation is allowed to complete. Use a small
    # number for unattended daily operation; resume state makes it safe.
    max_sessions_per_run: int = _env_int("PITWALL_MAX_SESSIONS_PER_RUN", 2)

    # Future ingestion should wait until the session is plausibly finished.
    # Race/qualifying dates come from the FastF1 schedule; this is an extra
    # safety buffer before attempting acquisition.
    session_completion_buffer_hours: float = _env_float(
        "PITWALL_SESSION_COMPLETION_BUFFER_HOURS", 6.0
    )

    oracle_host: str = os.getenv("ORACLE_HOST", "")
    oracle_user: str = os.getenv("ORACLE_USER", "")
    oracle_ssh_key: Path | None = (
        Path(os.environ["ORACLE_SSH_KEY"])
        if os.getenv("ORACLE_SSH_KEY")
        else None
    )
    oracle_cache_dir: str = os.getenv("ORACLE_CACHE_DIR", "/opt/pitwall/cache")
    oracle_manifest_path: str = os.getenv(
        "ORACLE_MANIFEST_PATH", "/opt/pitwall/metadata/session_manifest.json"
    )
    oracle_staging_dir: str = os.getenv(
        "ORACLE_STAGING_DIR", "/opt/pitwall/cache/.staging"
    )
    sync_to_oracle: bool = _env_bool("PITWALL_SYNC_TO_ORACLE", True)

    # Version policy. We detect newer releases but never silently upgrade a
    # running archive. An explicit dependency update command is safer.
    fail_on_newer_fastf1: bool = _env_bool(
        "PITWALL_FAIL_ON_NEWER_FASTF1", False
    )


config = IngestionConfig()
