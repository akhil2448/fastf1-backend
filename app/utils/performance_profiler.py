from __future__ import annotations

import cProfile
import json
import os
import pstats
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


BASE_PROFILE_DIR = Path("performance_profiles")

# Example:
#
# PERF_CHECKPOINT=race_analyzer
# PERF_RUN=optimization_3
#
# Produces:
#
# performance_profiles/
# └── race_analyzer/
#     └── optimization_3/
#         └── 20260830_203015_123456/
#
CHECKPOINT_NAME = (
    os.getenv(
        "PERF_CHECKPOINT",
        "current",
    ).strip()
    or "current"
)

RUN_NAME = (
    os.getenv(
        "PERF_RUN",
        "current",
    ).strip()
    or "current"
)


_CURRENT_RUN_DIR: ContextVar[Path | None] = ContextVar(
    "_CURRENT_RUN_DIR",
    default=None,
)


def _create_run_directory() -> Path:
    """
    Create a unique directory for one profiling execution.
    """

    run_root = (
        BASE_PROFILE_DIR
        / CHECKPOINT_NAME
        / RUN_NAME
    )

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
    Profile one API request.

    Output:

        performance_profiles/
            <checkpoint>/
                <run>/
                    <timestamp>/
                        <name>.prof
                        <name>.txt
                        snapshots/
                            ...
    """

    profiler = cProfile.Profile()

    run_dir = _create_run_directory()

    snapshots_dir = (
        run_dir / "snapshots"
    )

    snapshots_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    token = _CURRENT_RUN_DIR.set(
        run_dir
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

        _CURRENT_RUN_DIR.reset(token)


def save_json_snapshot(
    name: str,
    payload: Any,
) -> Path:
    """
    Save a canonical JSON representation for
    the current profiling request.
    """

    run_dir = _CURRENT_RUN_DIR.get()

    if run_dir is None:
        raise RuntimeError(
            "save_json_snapshot() must be called "
            "inside profile_request()."
        )

    snapshots_dir = (
        run_dir / "snapshots"
    )

    snapshots_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_name = (
        name
        .replace("/", "_")
        .replace(" ", "_")
    )

    path = (
        snapshots_dir
        / f"{safe_name}.json"
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