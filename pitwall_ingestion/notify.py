from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .config import config


def write_summary(summary: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def mac_notification(title: str, message: str) -> None:
    """Best-effort macOS notification; never breaks ingestion if unavailable."""
    if platform.system() != "Darwin":
        return
    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                f'display notification {json.dumps(message)} with title {json.dumps(title)}',
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception:
        pass


def publish_oci_notification(title: str, body: str) -> None:
    """Publish an email notification through OCI Notifications.

    This runs on Oracle. The OCI CLI authenticates using the VM's
    Instance Principal. PitWall never stores an OCI API private key,
    email password, or SMTP credential.
    """
    if not config.oci_notifications_topic_ocid:
        raise RuntimeError(
            "OCI_NOTIFICATIONS_TOPIC_OCID is not configured. "
            "Cannot publish scheduler email."
        )

    configured_oci = config.oci_cli_path.strip()
    oci = configured_oci or shutil.which("oci")

    if not oci:
        raise RuntimeError(
            "OCI CLI was not found. Set OCI_CLI_PATH or add the OCI CLI to PATH."
        )

    command = [
        oci,
        "ons",
        "message",
        "publish",
        "--auth",
        "instance_principal",
        "--region",
        "us-chicago-1",
        "--topic-id",
        config.oci_notifications_topic_ocid,
        "--title",
        title,
        "--body",
        body,
    ]

    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "OCI notification publish timed out after 60 seconds."
        ) from exc
    except OSError as exc:
        raise RuntimeError(
            f"Failed to execute OCI CLI at '{oci}': {exc}"
        ) from exc

    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        detail = stderr or stdout or f"exit code {result.returncode}"
        raise RuntimeError(
            f"OCI notification publish failed: {detail}"
        )

def notify_run(summary: dict[str, Any], mode: str) -> None:
    if summary["failed"]:
        mac_notification(
            f"PitWall {mode} ingestion failed",
            (
                f"Processed {summary['processed']}; "
                f"succeeded {summary['succeeded']}; "
                f"failed {summary['failed']}"
            ),
        )
    elif summary["succeeded"]:
        mac_notification(
            f"PitWall {mode} ingestion succeeded",
            (
                f"Processed {summary['processed']}; "
                f"completed {summary['succeeded']}"
            ),
        )
    elif summary["stopped"]:
        mac_notification(
            f"PitWall {mode} ingestion stopped",
            "The run stopped safely and will resume from the manifest next time.",
        )
