from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable

import pandas as pd
import fastf1


@dataclass(frozen=True)
class PlannedSession:
    key: str
    year: int
    round_number: int
    session_type: str
    event_name: str
    session_date: datetime | None


def _as_utc(value) -> datetime | None:
    if pd.isna(value):
        return None
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.to_pydatetime().astimezone(timezone.utc)


def build_schedule(
    years: Iterable[int],
    *,
    only_sessions_ended_by: datetime | None = None,
) -> list[PlannedSession]:
    now = only_sessions_ended_by or datetime.now(timezone.utc)
    planned: list[PlannedSession] = []

    for year in years:
        df = fastf1.get_event_schedule(year)
        df = df[df["RoundNumber"] > 0]

        for _, row in df.iterrows():
            round_number = int(row["RoundNumber"])
            event_name = str(row["EventName"])

            q_date = _as_utc(row.get("Session4DateUtc"))
            r_date = _as_utc(row.get("Session5DateUtc"))

            for code, session_date in (("Q", q_date), ("R", r_date)):
                if session_date is None:
                    continue
                planned.append(
                    PlannedSession(
                        key=f"{year}-{round_number:02d}-{code}",
                        year=year,
                        round_number=round_number,
                        session_type=code,
                        event_name=event_name,
                        session_date=session_date,
                    )
                )

    return sorted(
        planned,
        key=lambda x: (
            x.year,
            x.round_number,
            0 if x.session_type == "Q" else 1,
        ),
    )
