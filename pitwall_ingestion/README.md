# PitWall FastF1 ingestion pipeline

This package maintains PitWall's verified Race + Qualifying FastF1 archive.

It has two distinct workflows:

- **Historical ingestion** — one-time local acquisition for the archive.
- **Future ingestion** — ongoing local acquisition of newly completed sessions, with incremental Oracle synchronization.

Sprint sessions are excluded for now.

## Architecture

FastF1 acquisition happens on the local Mac because the Oracle VM must not make direct live-timing API calls. The Oracle VM runs only a lightweight scheduler that reads server-side metadata and sends email notifications.

```text
Oracle VM
  daily cron
      |
      v
future_scheduler.py
      |
      +--> schedule_snapshot.json
      +--> session_manifest.json
      |
      v
OCI Notifications -> email

Mac
  future_ingestion.py
      |
      v
FastF1 local acquisition
      |
      v
session validation
      |
      v
rsync only the completed session to Oracle
      |
      v
remote verification
      |
      v
manifest update
      |
      v
delete local session directory
```

The scheduler never calls FastF1 or the F1 live-timing endpoint.

## Future-safe schedule handling

The Oracle scheduler uses a locally fetched schedule snapshot instead of calling FastF1.

This matters at the start of a new season. Neither the scheduler nor the application can know exactly when a future F1 season's schedule becomes available.

For example, when the calendar moves to 2027 and no 2027 schedule exists in the server snapshot, the scheduler sends an email saying that the 2027 schedule needs to be loaded locally.

Run this on the Mac once FastF1 can see the new season:

```bash
python pitwall_ingestion/scripts/refresh_schedule.py --year 2027
```

The script fetches the schedule locally and atomically publishes the updated snapshot to Oracle.

The scheduler checks only the current calendar year for a missing schedule. It does not guess a release date.

## Consolidated email behavior

The Oracle scheduler does not send one email per race/session.

It builds the current backlog from:

- sessions whose scheduled time is older than the configured completion buffer;
- sessions that are not `complete` in the Oracle manifest;
- missing current-season schedule information.

A changed backlog triggers one email immediately.

If the backlog remains unchanged, a reminder is sent only after:

```text
PITWALL_PENDING_REMINDER_INTERVAL_HOURS
```

Default: 72 hours.

When a session is successfully synced and marked `complete`, it disappears from future reminder emails automatically.

If there are five missed race weekends, the email contains one consolidated list rather than five separate messages.

## FastF1 acquisition safety

FastF1's own request-level rate limiter is never modified.

PitWall adds an additional:

```text
PITWALL_SESSION_COOLDOWN_SECONDS=120
```

delay between completed session attempts.

This is deliberately conservative.

Each future session goes through:

1. FastF1 `session.load()`;
2. filesystem validation;
3. logical PitWall validation;
4. Oracle staging transfer;
5. atomic publish;
6. remote file-count and byte-count verification;
7. manifest update;
8. local session-directory cleanup.

The local session is deleted only after the Oracle copy is verified and the manifest has been pushed successfully.

The monolithic `fastf1_http_cache.sqlite` is not recopied to Oracle for every new session.

## Resuming after interruption

The manifest is checkpointed after each session.

If the Mac is shut down or the process is interrupted:

- a session left in `fetching` state becomes retryable on the next run;
- already-complete sessions are skipped;
- already-synced sessions are imported from the Oracle manifest before local work begins.

Run the same command again.

## Schedule snapshot

Default local file:

```text
.pitwall-ingestion/schedule_snapshot.json
```

Default Oracle file:

```text
/opt/pitwall/metadata/schedule_snapshot.json
```

Refreshing a year merges the new schedule into the existing snapshot so that refreshing 2027 does not remove 2026.

## Manifest

Default local future manifest:

```text
.pitwall-ingestion/future_manifest.json
```

Default Oracle manifest:

```text
/opt/pitwall/metadata/session_manifest.json
```

The manifest is the source of truth for whether a Race/Qualifying session has been successfully processed and synced.

After the historical archive is copied to Oracle, publish the final historical manifest once before removing the local archive:

```bash
python pitwall_ingestion/scripts/publish_manifest.py --manifest .pitwall-ingestion/historical_manifest.json
```

The Oracle scheduler intentionally does not treat a missing manifest as an empty archive. It sends a setup notification instead, preventing a false backlog of every completed historical session.

## Oracle email notifications

The Oracle scheduler publishes through OCI Notifications using the OCI CLI.

Set on Oracle:

```text
OCI_NOTIFICATIONS_TOPIC_OCID=<topic OCID>
```

The OCI CLI must be installed and authenticated on the Oracle VM.

Create an OCI Notifications topic, then create an Email subscription for the topic and confirm the subscription from the email Oracle sends.

Oracle documents email subscriptions and the CLI publish command here:

- Email subscription: https://docs.oracle.com/en-us/iaas/Content/Notification/Tasks/create-subscription-email.htm
- Publish message: https://docs.oracle.com/en-us/iaas/Content/Notification/Tasks/publishingmessages.htm

## Oracle scheduler

Default scheduler state:

```text
/opt/pitwall/metadata/future_scheduler_state.json
```

The scheduler is intentionally FastF1-free.

Example cron entry on Oracle:

```cron
17 8 * * * cd /opt/pitwall/ingestion && /usr/bin/python3 pitwall_ingestion/scripts/future_scheduler.py >> /opt/pitwall/metadata/future_scheduler.log 2>&1
```

The exact Python path should match the Python environment installed for the ingestion package.

The scheduler can be manually tested:

```bash
python pitwall_ingestion/scripts/future_scheduler.py --force-email
```

## Local commands

Fetch/refresh a new season schedule and publish it:

```bash
python pitwall_ingestion/scripts/refresh_schedule.py --year 2027
```

Future ingestion with Oracle sync:

```bash
python pitwall_ingestion/scripts/future_ingestion.py
```

Future ingestion with a temporary safety cap:

```bash
python pitwall_ingestion/scripts/future_ingestion.py --max-sessions 2
```

Future dry run without Oracle sync or local cleanup:

```bash
python pitwall_ingestion/scripts/future_ingestion.py --year 2026 --no-sync --no-cleanup
```

Historical ingestion:

```bash
python pitwall_ingestion/scripts/historical_ingestion.py --start-year 2018 --end-year 2026 --max-sessions 2
```

## Environment

```text
FASTF1_CACHE_DIR=cache
PITWALL_INGESTION_METADATA_DIR=.pitwall-ingestion

PITWALL_START_YEAR=2018
PITWALL_CURRENT_YEAR=2026

PITWALL_SESSION_COOLDOWN_SECONDS=120
PITWALL_MAX_SESSIONS_PER_RUN=2
PITWALL_SESSION_COMPLETION_BUFFER_HOURS=48
PITWALL_PENDING_REMINDER_INTERVAL_HOURS=72

ORACLE_HOST=...
ORACLE_USER=...
ORACLE_SSH_KEY=/path/to/key
ORACLE_CACHE_DIR=/opt/pitwall/cache
ORACLE_STAGING_DIR=/opt/pitwall/cache/.staging
ORACLE_MANIFEST_PATH=/opt/pitwall/metadata/session_manifest.json
ORACLE_SCHEDULE_PATH=/opt/pitwall/metadata/schedule_snapshot.json
ORACLE_SCHEDULER_STATE_PATH=/opt/pitwall/metadata/future_scheduler_state.json

OCI_NOTIFICATIONS_TOPIC_OCID=...
```

Historical ingestion remains local-only until you intentionally transfer the full archive.

## Cache analysis

`analyze_existing_cache.py` can be used to audit the physical cache and identify missing required resources.

A folder existing by itself is not enough. The cache analyzer records required resources and whether they are present.

The generated analysis JSON is operational output and should not be committed to Git.

## Dependency versions

The run checks the installed FastF1 version against PyPI and records the installed version for completed sessions.

It does not silently upgrade FastF1 during ingestion.

Use:

```bash
python pitwall_ingestion/scripts/update_dependencies.py
```

for an explicit dependency update.

PitWall imports the Ergast-compatible API through `fastf1.ergast`; there is no separate Ergast package to upgrade in this ingestion package.
