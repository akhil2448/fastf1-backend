# PitWall FastF1 ingestion pipeline

This package provides the local data-ingestion foundation for PitWall's verified Race + Qualifying archive. Sprint sessions are excluded for now.

## Entry points

- `scripts/historical_ingestion.py` — historical 2018 → selected year, local-only. It intentionally does not upload to Oracle while the archive is being built.
- `scripts/future_ingestion.py` — current season. It checks/synchronizes the Oracle manifest and uploads verified sessions incrementally.

Both use the same validation, manifest, rate-safety, logging and version-checking code.

## Rate-limit safety

FastF1's own request-level limiter is never changed. A separate configurable cooldown is applied **between complete session attempts**, not between FastF1's internal HTTP requests. This is deliberately conservative.

Default:

```text
PITWALL_SESSION_COOLDOWN_SECONDS=120
PITWALL_MAX_SESSIONS_PER_RUN=2
```

The scheduler is resumable. If the Mac is shut down, the manifest is already checkpointed. On the next run, stale `fetching` sessions become retryable `incomplete` sessions.

## Session completion

A folder existing is not enough. A session must pass:

1. required FastF1 cache-resource validation;
2. logical FastF1/PitWall property validation;
3. fastest-lap X/Y telemetry validation for the track map;
4. Race-only weather/race-control/total-laps validation.

Qualifying Phase 1 excludes weather and race-control requirements.

## Oracle publishing

Future ingestion transfers a verified session into an Oracle staging directory using `rsync`, then atomically publishes the directory. The server-side manifest is updated after successful processing.

Required environment variables for Oracle sync:

```text
ORACLE_HOST=...
ORACLE_USER=...
ORACLE_SSH_KEY=/path/to/key
ORACLE_CACHE_DIR=/opt/pitwall/cache
ORACLE_STAGING_DIR=/opt/pitwall/cache/.staging
ORACLE_MANIFEST_PATH=/opt/pitwall/metadata/session_manifest.json
```

The historical process remains local-only until you intentionally perform the one-time full archive transfer.

## Local environment

```text
FASTF1_CACHE_DIR=cache
PITWALL_INGESTION_METADATA_DIR=.pitwall-ingestion
PITWALL_START_YEAR=2018
PITWALL_CURRENT_YEAR=2026
PITWALL_SESSION_COOLDOWN_SECONDS=120
PITWALL_MAX_SESSIONS_PER_RUN=2
PITWALL_SESSION_COMPLETION_BUFFER_HOURS=6
```

## Commands

Historical, two sessions per run:

```bash
python scripts/historical_ingestion.py --start-year 2018 --end-year 2026 --max-sessions 2
```

Future season with Oracle sync:

```bash
python scripts/future_ingestion.py --year 2026 --max-sessions 2
```

Future dry run without Oracle sync:

```bash
python scripts/future_ingestion.py --year 2026 --no-sync --max-sessions 1
```

## Notifications and logs

Every run produces:

```text
.pitwall-ingestion/historical_last_run.json
.pitwall-ingestion/future_last_run.json
```

On macOS, the scripts also show a best-effort desktop notification after a successful or failed run. Console output remains the primary detailed report.

## Dependency versions

The run checks the installed FastF1 version against PyPI and records the installed version for each completed session. It does **not** silently upgrade FastF1 during ingestion, because doing so could create an uncontrolled mixed-version archive.

Use:

```bash
python scripts/update_dependencies.py
```

to deliberately upgrade FastF1.

PitWall imports `Ergast` from `fastf1.ergast`; there is no separate Ergast package in the application to upgrade independently. The external Ergast-compatible API source should be treated as a separate runtime dependency and verified when we build the classification-data ingestion layer.
