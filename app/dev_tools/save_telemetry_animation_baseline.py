from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.services.session_cache_service import (
    get_loaded_session,
)

from app.services.telemetry_animation_chunk_writer import (
    generate_race_telemetry,
)


YEAR = 2026
ROUND = 11

OUTPUT_DIR = Path(
    "performance_baselines/telemetry_animation"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / f"baseline_{YEAR}_{ROUND}.json"
)


def main():

    print(
        f"Loading {YEAR} Round {ROUND}..."
    )

    session = get_loaded_session(
        YEAR,
        ROUND,
    )

    print()
    print(
        "Generating complete race telemetry..."
    )

    telemetry_data = generate_race_telemetry(
        session
    )

    print()
    print(
        "Writing canonical baseline JSON..."
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            telemetry_data,
            file,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )

    ##############################################################
    # SHA-256
    ##############################################################

    digest = hashlib.sha256()

    with OUTPUT_FILE.open(
        "rb"
    ) as file:

        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):

            digest.update(chunk)

    print()
    print("=" * 70)
    print("TELEMETRY ANIMATION BASELINE")
    print("=" * 70)

    print(
        "File:",
        OUTPUT_FILE,
    )

    print(
        "Size:",
        OUTPUT_FILE.stat().st_size,
        "bytes",
    )

    print(
        "SHA-256:",
        digest.hexdigest(),
    )

    print(
        "Frames:",
        len(
            telemetry_data["frames"]
        ),
    )

    print(
        "Timing events:",
        len(
            telemetry_data["timingEvents"]
        ),
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()