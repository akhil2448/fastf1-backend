from __future__ import annotations

import json
import urllib.request
from importlib.metadata import PackageNotFoundError, version


def installed_version(package: str) -> str | None:
    try:
        return version(package)
    except PackageNotFoundError:
        return None


def latest_pypi_version(package: str, timeout: int = 10) -> str | None:
    url = f"https://pypi.org/pypi/{package}/json"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "PitWall-cache-ingestion/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
        return payload["info"]["version"]
    except Exception:
        return None


def check_versions() -> dict:
    fastf1_installed = installed_version("fastf1")
    fastf1_latest = latest_pypi_version("fastf1")

    # PitWall currently uses FastF1's bundled Ergast-compatible client:
    # from fastf1.ergast import Ergast
    # There is no separately installed `ergast` package to version here.
    return {
        "fastf1": {
            "installed": fastf1_installed,
            "latest": fastf1_latest,
            "update_available": bool(
                fastf1_installed
                and fastf1_latest
                and fastf1_installed != fastf1_latest
            ),
        },
        "ergast_client": {
            "provided_by": "fastf1.ergast.Ergast",
            "version_source": "FastF1 package",
        },
    }
