from __future__ import annotations

from typing import Any

import pandas as pd

from app.services.race_management.race_analyzer.corner_time_builder import (
    CornerTimeBuilder,
)
from app.services.race_management.race_analyzer.distribution_builder import (
    DistributionBuilder,
)
from app.services.race_management.race_analyzer.driving_phase_builder import (
    DrivingPhaseBuilder,
)
from app.services.race_management.race_analyzer.lift_coast_builder import (
    LiftCoastBuilder,
)
from app.services.race_management.race_analyzer.off_throttle_event_builder import (
    OffThrottleEventBuilder,
)
from app.services.race_management.race_analyzer.phase_context_builder import (
    PhaseContextBuilder,
)
from app.services.race_management.race_analyzer.zone_progress_builder import (
    ZoneProgressBuilder,
)

from app.services.race_management.race_analyzer.full_throttle_event_builder import (
    FullThrottleEventBuilder,
)
from app.services.race_management.race_analyzer.clipping_builder import (
    ClippingBuilder,
)


class LapAnalysisBuilder:
    """
    Runs the complete lap analysis pipeline.

    This class orchestrates the various builders while
    keeping each builder responsible for a single task.
    """

    @classmethod
    def build(
        cls,
        telemetry: pd.DataFrame,
        corner_zones: list[dict[str, Any]],
    ) -> dict[str, Any]:

        #
        # Split telemetry into driving phases.
        #
        phases = DrivingPhaseBuilder.build(
            telemetry,
        )

        #
        # Add neighbouring phase context.
        #
        phases = PhaseContextBuilder.build(
            phases,
        )

        #
        # Determine where each phase occurs relative
        # to the official corner zones.
        #
        zone_progress = ZoneProgressBuilder.build(
            phases,
            corner_zones,
        )
        
        #
        # Group continuous full-throttle phases.
        #
        full_throttle_events = (
            FullThrottleEventBuilder.build(
                phases,
                telemetry,
                zone_progress,
            )
        )

        #
        # Detect clipping.
        #
        clipping_events = (
            ClippingBuilder.build(
                full_throttle_events,
            )
        )

        #
        # Group continuous off-throttle phases.
        #
        off_throttle_events = (
            OffThrottleEventBuilder.build(
                phases,
                telemetry,
                zone_progress,
            )
        )

        #
        # Detect lift-and-coast.
        #
        classified_events = (
            LiftCoastBuilder.build(
                off_throttle_events,
            )
        )

        #
        # Calculate total cornering time.
        #
        corner_time = CornerTimeBuilder.build(
            telemetry,
            corner_zones,
        )

        #
        # Build throttle/brake distribution.
        #
        distribution = DistributionBuilder.build(
            phases,
            corner_time,
            classified_events,
            clipping_events,
        )

        return {

            #
            # Primary API output
            #
            "distribution": distribution,

            #
            # Internal analysis
            #
            "cornerZones": corner_zones,

            "cornerTime": corner_time,

            "phases": phases,

            "zoneProgress": zone_progress,

            "offThrottleEvents": off_throttle_events,

            "liftCoastEvents": classified_events,
            
            "fullThrottleEvents": full_throttle_events,

            "clippingEvents": clipping_events, 
        }