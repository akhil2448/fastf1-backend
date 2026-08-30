from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pitwall_ingestion.manifest import Manifest
from pitwall_ingestion.sync import push_manifest
from pitwall_ingestion.config import config


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publish a local PitWall session manifest to Oracle."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=config.metadata_dir / "historical_manifest.json",
        help="Local manifest to publish.",
    )
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"Manifest does not exist: {args.manifest}", flush=True)
        return 1

    manifest = Manifest(args.manifest)
    print(
        f"Publishing {args.manifest} with {len(manifest.data.get('sessions', {}))} sessions...",
        flush=True,
    )
    push_manifest(args.manifest)
    print(f"Manifest uploaded to {config.oracle_manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
