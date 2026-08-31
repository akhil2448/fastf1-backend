# PITWALL BACKEND

### FastAPI + FastF1 data and analysis engine

The PitWall backend powers the race simulation and Performance Lab experiences. It loads historic Formula 1 session data through FastF1, maintains persistent session/cache state, transforms timing and telemetry into application-specific models, and exposes the results through a FastAPI HTTP API.

The backend is designed around time-series processing rather than CRUD operations: most endpoints derive synchronized race, telemetry, track-state, and driver-analysis data from a loaded FastF1 session.

> **Note:** PitWall is an independent fan/engineering project and is not affiliated with Formula 1, the FIA, or any Formula 1 team.

---

# Responsibilities

```text
FastF1 Session Data
        │
        ▼
  Session Cache
        │
        ├───────────────┐
        │               │
        ▼               ▼
 Race Simulation   Performance Lab
        │               │
        │        ┌──────┴─────────┐
        │        │                │
        ▼        ▼                ▼
Telemetry   Ultimate Pace   Race Management
            / Qualifying    / Race Analysis
            Comparison
        │        │                │
        └────────┴────────────────┘
                 │
                 ▼
              FastAPI
                 │
                 ▼
             Angular UI
```

---

# Feature Domains

## 1. Race Simulation

The simulation endpoints provide everything required to reconstruct a historic Grand Prix in the browser:

- Race schedule and event selection
- Qualifying results
- Starting grid and starting tyre information
- Race lap/timing metadata
- Weather
- Race-control messages
- Track status
- Circuit/track-map geometry
- Full-race telemetry animation snapshots
- High-resolution driver telemetry
- Final FIA classification
- Driver and constructor championship standings at race end

## 2. Performance Lab

Performance Lab is split into two analysis modes.

### Ultimate Pace

Compare up to two drivers from the same qualifying session using synchronized telemetry and track position.

The comparison pipeline supports Q1, Q2, and Q3 and exposes data used to visualize:

- Speed
- RPM
- Throttle
- Brake
- Lap delta
- Track position
- Sector timing

### Race Management

Analyze race laps in the context of tyre wear, stint progression, race pace, traffic, wake effects, DRS usage, and lap consistency.

The analysis pipeline identifies usable laps, scores compatibility, builds traffic information, selects representative laps, and produces synchronized race-lap comparison data.

### Race Analyzer

Race Analyzer provides a lap-by-lap performance view for one or two selected drivers, including detailed race-analysis metadata and driver-focused comparisons.

---

# API

The API is grouped by product experience rather than by implementation class.

## Race Simulation API

| Endpoint | Purpose |
|---|---|
| `GET /api/schedule/{year}` | Return the season race schedule for race selection |
| `GET /api/qualifying/{year}/{round}` | Qualifying results and race starting grid data |
| `GET /api/starting-grid/{year}/{round}` | Official starting grid and starting tyre information |
| `GET /api/race/{year}/{round}` | Race metadata, lap timing, tyre/pit information, classification and championship tables |
| `GET /api/weather/{year}/{round}` | Weather data used during the race simulation |
| `GET /api/race-control/{year}/{round}` | FIA-style race-control messages |
| `GET /api/track-status/{year}/{round}` | Yellow flags, VSC, safety-car, red-flag and related track-status data |
| `GET /api/track-map/{year}/{round}` | Track coordinates used to render the circuit |
| `GET /api/telemetry/{year}/{round}` | Cached per-second race animation snapshots for a requested time window |
| `GET /api/driver-telemetry/{year}/{round}/{driver}` | High-resolution telemetry for one driver over a requested time window |

Telemetry animation requests are limited to ten-minute windows. The complete race telemetry is generated once per race and subsequent requests are served from the in-memory race telemetry cache.

## Performance Lab API

| Endpoint | Purpose |
|---|---|
| `GET /api/ultimate-pace/{year}/{round}` | Drivers available for Q1/Q2/Q3 comparison |
| `GET /api/race-management/{year}/{round}/drivers` | Race Management driver/stint/tyre overview |
| `GET /api/race-management/{year}/{round}` | Compare selected race laps for two drivers / fetch recommended analysis payload |
| `GET /api/race-management/{year}/{round}/{driver}` | Analyze race laps for a single driver |
| `GET /api/qualifying-comparison/{year}/{round}/{session_part}` | Synchronized qualifying-lap comparison |
| `GET /api/race-comparison/{year}/{round_number}` | Synchronized race-lap comparison |
| `GET /api/race-analyzer/{year}/{round}` | Lap-level race performance analysis for one or two drivers |

Example:

```text
GET /api/qualifying-comparison/2026/1/Q3?driverA=RUS&driverB=ANT
```

```text
GET /api/race-comparison/2026/1?driverA=COL&lapA=35&driverB=PER&lapB=21
```

```text
GET /api/race-analyzer/2026/1?driverA=VER&driverB=LEC
```

---

# Session Loading and Caching

FastF1 session loading is expensive and the upstream data source is not assumed to be reliably reachable from the production server. PitWall therefore separates **persistent FastF1 caching** from **application-level session caching**.

### Persistent FastF1 cache

The cache directory is configurable through:

```text
FASTF1_CACHE_DIR
```

Defaults:

```text
Local:      cache
Production: /app/cache
```

The production Docker deployment mounts the persistent FastF1 cache into `/app/cache`.

### Application session cache

Loaded race and qualifying sessions are held in process memory so repeated endpoint requests do not reload the same FastF1 session.

```text
Request
   │
   ▼
get_loaded_session(year, round)
   │
   ├── cache hit ─────────────► return existing Session
   │
   └── cache miss
         │
         ▼
      FastF1 load
         │
         ▼
      session cache
```

Session loading is guarded so concurrent requests do not unnecessarily load the same race multiple times.

---

# Telemetry Architecture

Race telemetry is transformed into a representation optimized for playback rather than repeatedly serving raw FastF1 telemetry.

```text
FastF1 telemetry
       │
       ▼
Per-driver processing
       │
       ├── Lap assignment
       ├── Distance calculation
       ├── Resampling
       ├── Track position
       ├── Race distance
       ├── Timing-loop events
       └── Per-second snapshots
       │
       ▼
Complete race telemetry
       │
       ▼
In-memory race cache
       │
       ├── 0–600
       ├── 601–1200
       ├── 1201–1800
       └── ...
```

The animation API returns only the requested window after the race-wide telemetry has been generated and cached.

---

# Race Management Architecture

Race Management is intentionally decomposed into reusable analysis services.

```text
Loaded FastF1 Session
        │
        ├── Race Timeline
        ├── Race Progress Collection
        ├── Track Length
        │
        ▼
   Driver Stints
        │
        ├── Lap validation
        ├── Tyre / stint metadata
        ├── Position stability
        ├── Lap-time consistency
        ├── Sector consistency
        ├── Traffic index
        ├── Wake / dirty-air analysis
        ├── DRS analysis
        └── Representative lap analysis
```

The optimization work for this domain focused on reusing race-wide structures instead of rebuilding them repeatedly and replacing expensive repeated scans with indexed/vectorized approaches where correctness could be preserved.

---

# Race Analyzer Architecture

Race Analyzer is broken into specialized builders so individual concepts can be analyzed independently:

```text
Race Analyzer
│
├── Race metadata
├── Corner zones
├── Corner timing
├── Driving phases
├── Full-throttle events
├── Lift / coast analysis
├── Off-throttle events
├── Lap distributions
├── Zone progress
└── Lap analysis
```

The service accepts one or two driver codes and returns a structured payload consumed by the frontend comparison visualizations.

---

# Performance Engineering

PitWall's backend has undergone a benchmark-driven optimization pass with frozen output baselines and regression tests.

## Telemetry animation

Full-race telemetry generation for a 22-driver 2026 race was measured at approximately:

```text
Original baseline:      ~36.0 s
Optimized generation:   ~12.5 s
Improvement:             ~65%
```

The optimized result was validated against a canonical baseline using:

```text
22 drivers
125,215 telemetry chunks checked
85,015 timing events checked
Baseline JSON == Optimized JSON
```

The production design also caches the generated race telemetry, so subsequent ten-minute telemetry-window requests are served in roughly sub-second time on the production Oracle environment after the initial generation.

## Optimization philosophy

Performance changes were accepted only when they preserved the generated output. The workflow was:

```text
Measure
  ↓
Identify dominant stage
  ↓
Optimize one stage
  ↓
Freeze baseline
  ↓
Run regression comparison
  ↓
Verify identical output
  ↓
Benchmark again
```

This prevented performance work from silently changing race-state or telemetry behavior.

---

# Production Architecture

The deployed backend runs in Docker on an Oracle Cloud VM with persistent block storage for the FastF1 cache.

```text
Cloudflare Pages
      │
      ▼
   Frontend
      │ HTTPS / /api
      ▼
     Nginx
      │
      ▼
 FastAPI / Uvicorn
      │
      ├── In-memory session cache
      ├── In-memory telemetry cache
      │
      ▼
 /app/cache
      │
      ▼
Oracle Block Storage
(persistent FastF1 cache)
```

The application uses a single Uvicorn worker in the current production deployment. This avoids duplicating process-local FastF1/session and telemetry caches across workers.

---

# Configuration

The backend reads configuration from environment variables.

| Variable | Purpose | Default |
|---|---|---|
| `ENV` | Runtime environment | `development` |
| `FASTF1_CACHE_DIR` | FastF1 persistent cache directory | `cache` |
| `FRONTEND_URL` | Allowed frontend origin for CORS | `http://localhost:4200` |
| `LOG_LEVEL` | Application logging level | `INFO` |

Example local configuration:

```env
ENV=development
FASTF1_CACHE_DIR=cache
FRONTEND_URL=http://localhost:4200
LOG_LEVEL=INFO
```

Example production configuration:

```env
ENV=production
FASTF1_CACHE_DIR=/app/cache
FRONTEND_URL=https://pitwallf1.pages.dev
LOG_LEVEL=INFO
```

---

# Local Development

## Prerequisites

- Python 3.12+
- FastF1
- FastAPI / Uvicorn
- A populated FastF1 cache for races you want to run without upstream access

## Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Start the API

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# Docker / Production Notes

The production container mounts the persistent FastF1 cache into:

```text
/app/cache
```

and sets:

```text
FASTF1_CACHE_DIR=/app/cache
```

The persistent cache is important because the production host may not be able to access the upstream Formula 1 data services directly. The application is therefore designed to operate from the pre-populated FastF1 cache when deployed.

---

# Development Tools

The backend repository contains a dedicated `app/dev_tools` area used to inspect and validate analysis behavior without changing production services.

Examples include tooling for:

- telemetry inspection
- race-management validation
- race-analyzer inspection
- track-status mapping
- driving-phase analysis
- corner analysis
- lap-analysis validation
- telemetry alignment
- performance benchmarking
- canonical baseline generation
- regression comparison

The performance work used these tools to compare optimized output against frozen baseline JSON rather than relying on timing measurements alone.

---

# Correctness and Data Handling

FastF1 exposes pandas DataFrames and timedelta values that are treated as canonical internal session data.

An important production correctness rule is to avoid mutating session-owned DataFrames when formatting data for an API response. For example, weather data is copied before converting timedelta values into API-friendly strings so that another endpoint such as Race Analyzer continues to receive canonical `Timedelta` values.

```text
session.weather_data
        │
        ├── canonical session data
        │
        └── copy()
              │
              ▼
        API formatting
```

This protects shared session state across endpoints.

---

# Project Structure

```text
app/
├── api/
│   └── routes.py
├── config/
│   ├── settings.py
│   └── fastf1_config.py
├── dev_tools/
│   └── inspection, benchmarks and regression tools
├── services/
│   ├── race_management/
│   │   ├── analysis services
│   │   ├── race analyzer
│   │   ├── traffic / wake analysis
│   │   ├── race progress
│   │   └── stint / lap analysis
│   ├── telemetry services
│   ├── race / classification services
│   ├── comparison services
│   └── session / cache services
└── utils/
    ├── time utilities
    ├── JSON utilities
    └── race-time utilities
```

---

# Technology Stack

| Area | Technology |
|---|---|
| API | FastAPI |
| ASGI server | Uvicorn |
| F1 data | FastF1 |
| Data processing | pandas, NumPy |
| Runtime | Python |
| Persistence/cache | FastF1 cache + Oracle Block Storage |
| Containerization | Docker |
| Reverse proxy | Nginx |
| Frontend consumer | Angular |

---

# API Design Principles

The backend is organized around a few principles:

### Session-first processing

A loaded FastF1 session is treated as the source of truth for race data.

### Reuse race-wide structures

Expensive structures such as timelines, race progress collections, and track metadata are built once when practical and reused by downstream analyzers.

### Domain-specific services

Telemetry, race management, comparison, classification, and race-analyzer logic are kept in separate services instead of concentrating everything inside API routes.

### Output-preserving optimization

Performance improvements are accepted only after validating that the generated output remains identical to the baseline for the scenarios being optimized.

### Cache before recomputation

The API prefers persistent FastF1 cache and application-level session/telemetry caches before performing expensive processing again.

---

# Known Production Constraint

The production environment may not have direct access to upstream Formula 1 data services. The deployed system therefore depends on a pre-populated persistent FastF1 cache and should not be treated as a service that can freely download arbitrary new sessions from the production VM.

When adding a new season/race to production, populate and validate its FastF1 cache before relying on the corresponding endpoint.

---

# PitWall in one sentence

> **A FastAPI/FastF1 time-series engine that transforms historic Formula 1 session data into synchronized race replay, telemetry, comparison, and performance-analysis APIs.**
