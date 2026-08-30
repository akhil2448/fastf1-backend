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

# Examples:
# PERF_RUN=baseline
# PERF_RUN=optimization_1
# PERF_RUN=optimization_2
# PERF_RUN=optimization_3
RUN_NAME = os.getenv(
    "PERF_RUN",
    "current",
).strip() or "current"


def _create_run_directory() -> Path:
    """
    Create a unique directory for each profiling run.

    Example:
        performance_profiles/
            optimization_3/
                20260830_180001/
    """

    run_root = BASE_PROFILE_DIR / RUN_NAME
    run_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    run_dir = run_root / timestamp
    run_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    return run_dir


@contextmanager
def profile_request(
    name: str,
) -> Iterator[None]:
    """
    Profile one request and store all output in its own
    unique run directory.

    Example:
        performance_profiles/
            optimization_3/
                20260830_180001/
                    race_analyzer_2026_2_ANT_RUS.prof
                    race_analyzer_2026_2_ANT_RUS.txt
                    snapshots/
    """

    profiler = cProfile.Profile()

    run_dir = _create_run_directory()

    snapshots_dir = run_dir / "snapshots"
    snapshots_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    profiler.enable()

    try:
        yield

    finally:
        profiler.disable()

        safe_name = (
            name
            .replace("/", "_")
            .replace(" ", "_")
        )

        profile_path = (
            run_dir
            / f"{safe_name}.prof"
        )

        text_path = (
            run_dir
            / f"{safe_name}.txt"
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
    Save a canonical JSON representation of the API output.

    The snapshot is saved under the most recently created
    profiling run directory.

    This does not modify the payload returned to the caller.
    """

    # Find the most recently created run directory.
    run_root = BASE_PROFILE_DIR / RUN_NAME

    if not run_root.exists():
        raise RuntimeError(
            "No profiling run directory exists. "
            "Call profile_request() before save_json_snapshot()."
        )

    run_directories = [
        path
        for path in run_root.iterdir()
        if path.is_dir()
    ]

    if not run_directories:
        raise RuntimeError(
            "No profiling run directory exists. "
            "Call profile_request() before save_json_snapshot()."
        )

    run_dir = max(
        run_directories,
        key=lambda path: path.stat().st_mtime_ns,
    )

    snapshots_dir = run_dir / "snapshots"
    snapshots_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        snapshots_dir
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