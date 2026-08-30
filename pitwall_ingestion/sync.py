from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path

from .config import config


def _require_oracle_config() -> None:
    missing = []
    if not config.oracle_host:
        missing.append("ORACLE_HOST")
    if not config.oracle_user:
        missing.append("ORACLE_USER")
    if config.oracle_ssh_key is None:
        missing.append("ORACLE_SSH_KEY")
    if missing:
        raise RuntimeError(
            "Oracle sync requested but configuration is missing: "
            + ", ".join(missing)
        )


def _ssh_base() -> list[str]:
    _require_oracle_config()
    return [
        "ssh",
        "-i",
        str(config.oracle_ssh_key),
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"{config.oracle_user}@{config.oracle_host}",
    ]


def run_ssh(command: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        _ssh_base() + [command],
        check=True,
        text=True,
        capture_output=True,
    )


def fetch_remote_manifest() -> str | None:
    result = run_ssh(
        f"test -f {shlex.quote(config.oracle_manifest_path)} && "
        f"cat {shlex.quote(config.oracle_manifest_path)} || true"
    )
    return result.stdout if result.stdout.strip() else None


def push_manifest(local_manifest_path: Path) -> None:
    _require_oracle_config()
    remote_dir = os.path.dirname(config.oracle_manifest_path)
    remote_tmp = config.oracle_manifest_path + ".tmp"

    run_ssh(f"mkdir -p {shlex.quote(remote_dir)}")

    subprocess.run(
        [
            "scp",
            "-i",
            str(config.oracle_ssh_key),
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=accept-new",
            str(local_manifest_path),
            f"{config.oracle_user}@{config.oracle_host}:{remote_tmp}",
        ],
        check=True,
    )

    run_ssh(
        f"mv -f {shlex.quote(remote_tmp)} {shlex.quote(config.oracle_manifest_path)}"
    )


def sync_session(session_dir: Path, relative_session_path: str) -> None:
    """Transfer a verified session to staging and atomically publish it.

    After the atomic move, verify remote file count and byte count against the
    local session. A successful return means it is safe for the caller to
    remove the local temporary session.
    """
    _require_oracle_config()

    remote_stage = (
        f"{config.oracle_staging_dir.rstrip('/')}/{relative_session_path}"
    )
    remote_final = (
        f"{config.oracle_cache_dir.rstrip('/')}/{relative_session_path}"
    )
    stage_parent = os.path.dirname(remote_stage)

    run_ssh(
        f"mkdir -p {shlex.quote(stage_parent)} && "
        f"rm -rf {shlex.quote(remote_stage)}"
    )

    ssh_command = " ".join(
        shlex.quote(x)
        for x in [
            "ssh",
            "-i",
            str(config.oracle_ssh_key),
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=accept-new",
        ]
    )

    subprocess.run(
        [
            "rsync",
            "-az",
            "--partial",
            "--checksum",
            "--human-readable",
            "-e",
            ssh_command,
            str(session_dir) + "/",
            f"{config.oracle_user}@{config.oracle_host}:{remote_stage}/",
        ],
        check=True,
    )

    # Do not expose a partial session to production.
    final_parent = os.path.dirname(remote_final)
    run_ssh(
        f"mkdir -p {shlex.quote(final_parent)} && "
        f"rm -rf {shlex.quote(remote_final)} && "
        f"mv {shlex.quote(remote_stage)} {shlex.quote(remote_final)}"
    )

    # Verify that the published remote directory contains exactly the same
    # file count and total byte size as the locally validated session.
    local_files = [
        p for p in session_dir.rglob("*")
        if p.is_file()
    ]
    local_file_count = len(local_files)
    local_size_bytes = sum(p.stat().st_size for p in local_files)

    remote_file_count = int(
        run_ssh(
            f"find {shlex.quote(remote_final)} -type f | wc -l"
        ).stdout.strip()
        or "0"
    )
    if remote_file_count != local_file_count:
        raise RuntimeError(
            f"Remote verification failed for {relative_session_path}: "
            f"file count local={local_file_count}, "
            f"remote={remote_file_count}"
        )

    # du -sb includes directory metadata. Compare the file total separately
    # by summing remote file sizes.
    remote_file_bytes = int(
        run_ssh(
            f"find {shlex.quote(remote_final)} -type f -printf '%s\n' "
            f"| awk '{{s+=$1}} END {{print s+0}}'"
        ).stdout.strip()
        or "0"
    )

    if remote_file_bytes != local_size_bytes:
        raise RuntimeError(
            f"Remote verification failed for {relative_session_path}: "
            f"file bytes local={local_size_bytes}, "
            f"remote={remote_file_bytes}"
        )


def push_schedule_snapshot(local_path: Path) -> None:
    """Publish a locally fetched schedule snapshot to Oracle atomically."""
    _require_oracle_config()
    remote_dir = os.path.dirname(config.oracle_schedule_path)
    remote_tmp = config.oracle_schedule_path + ".tmp"

    run_ssh(f"mkdir -p {shlex.quote(remote_dir)}")

    subprocess.run(
        [
            "scp",
            "-i",
            str(config.oracle_ssh_key),
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=accept-new",
            str(local_path),
            f"{config.oracle_user}@{config.oracle_host}:{remote_tmp}",
        ],
        check=True,
    )

    run_ssh(
        f"mv -f {shlex.quote(remote_tmp)} {shlex.quote(config.oracle_schedule_path)}"
    )


def transfer_whole_cache(local_cache_dir: Path) -> None:
    """One-time historical archive transfer after the local archive is verified."""
    _require_oracle_config()
    ssh_command = " ".join(
        shlex.quote(x)
        for x in [
            "ssh",
            "-i",
            str(config.oracle_ssh_key),
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=accept-new",
        ]
    )
    subprocess.run(
        [
            "rsync",
            "-az",
            "--partial",
            "--checksum",
            "--human-readable",
            "-e",
            ssh_command,
            str(local_cache_dir) + "/",
            f"{config.oracle_user}@{config.oracle_host}:{config.oracle_cache_dir.rstrip('/')}/",
        ],
        check=True,
    )
