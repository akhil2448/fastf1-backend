from __future__ import annotations

from bisect import bisect_right
from datetime import timedelta


class TelemetryAlignment:

    @staticmethod
    def build_time_index(samples) -> tuple[list[timedelta], list[int]]:
        """
        Build a timestamp/index representation for telemetry samples.

        The sample order is preserved exactly.
        """

        times = [
            sample.session_time
            for sample in samples
        ]

        indexes = list(
            range(len(samples))
        )

        return times, indexes

    @staticmethod
    def nearest_index(
        times: list[timedelta],
        target_time: timedelta,
    ) -> int | None:

        if not times:
            return None

        #
        # Match TelemetryCursor semantics:
        #
        # current = last sample whose time <= target
        # next    = first sample whose time > target
        #
        right = bisect_right(
            times,
            target_time,
        )

        current_index = right - 1

        #
        # Target occurs before the first sample.
        #
        if current_index < 0:
            return 0

        #
        # Target occurs at/after the final sample.
        #
        if current_index >= len(times) - 1:
            return len(times) - 1

        next_index = current_index + 1

        current_delta = abs(
            (
                times[current_index]
                - target_time
            ).total_seconds()
        )

        next_delta = abs(
            (
                times[next_index]
                - target_time
            ).total_seconds()
        )

        #
        # Preserve TelemetryCursor tie behavior:
        # current wins when the distances are equal.
        #
        if next_delta < current_delta:
            return next_index

        return current_index