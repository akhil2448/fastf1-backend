from __future__ import annotations

import cProfile
import json
import os
import pstats
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


BASE_PROFILE_DIR = Path("performance_profiles")

# Example:
# PERF_RUN=baseline
# PERF_RUN=optimization_1
# PERF_RUN=optimization_2
RUN_NAME = os.getenv(
    "PERF_RUN",
    "current",
).strip() or "current"

PROFILE_DIR = BASE_PROFILE_DIR / RUN_NAME
SNAPSHOT_DIR = PROFILE_DIR / "snapshots"

PROFILE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

SNAPSHOT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


@contextmanager
def profile_request(name: str) -> Iterator[None]:
    """
    Development-only profiler for a single request.

    Output:
        performance_profiles/<run>/
            <name>.prof
            <name>.txt
            snapshots/
                <name>.json
    """

    profiler = cProfile.Profile()

    profiler.enable()

    try:
        yield

    finally:
        profiler.disable()

        timestamp = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d_%H%M%S"
        )

        safe_name = (
            name
            .replace("/", "_")
            .replace(" ", "_")
        )

        profile_path = (
            PROFILE_DIR
            / f"{safe_name}_{timestamp}.prof"
        )

        text_path = (
            PROFILE_DIR
            / f"{safe_name}_{timestamp}.txt"
        )

        profiler.dump_stats(
            profile_path
        )

        with text_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            stats = pstats.Stats(
                profiler,
                stream=file,
            )

            stats.strip_dirs()
            stats.sort_stats("cumulative")
            stats.print_stats(150)


def save_json_snapshot(
    name: str,
    payload: Any,
) -> Path:
    """
    Save a canonical JSON representation
    of the API output.

    This does not modify the payload returned
    to the caller.
    """

    path = (
        SNAPSHOT_DIR
        / f"{name}.json"
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            payload,
            file,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )

    return path