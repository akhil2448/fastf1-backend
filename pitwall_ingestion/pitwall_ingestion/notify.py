from __future__ import annotations

import json
import platform
import subprocess
from pathlib import Path
from typing import Any


def write_summary(summary: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")


def mac_notification(title: str, message: str) -> None:
    """Best-effort macOS notification; never breaks ingestion if unavailable."""
    if platform.system() != "Darwin":
        return
    try:
        subprocess.run(
            ["osascript", "-e", f'display notification {json.dumps(message)} with title {json.dumps(title)}'],
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception:
        pass


def notify_run(summary: dict[str, Any], mode: str) -> None:
    if summary["failed"]:
        mac_notification(
            f"PitWall {mode} ingestion failed",
            f"Processed {summary['processed']}; succeeded {summary['succeeded']}; failed {summary['failed']}",
        )
    elif summary["succeeded"]:
        mac_notification(
            f"PitWall {mode} ingestion succeeded",
            f"Processed {summary['processed']}; completed {summary['succeeded']}",
        )
    elif summary["stopped"]:
        mac_notification(
            f"PitWall {mode} ingestion stopped",
            "The run stopped safely and will resume from the manifest next time.",
        )
