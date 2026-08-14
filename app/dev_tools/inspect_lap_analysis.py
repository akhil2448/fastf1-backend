from __future__ import annotations

import fastf1

from app.services.race_management.race_analyzer.lap_analysis_builder import (
    LapAnalysisBuilder,
)

CACHE_DIR = "cache"

#
# Test combinations
#
# 2023
#   Monaco    = 6
#   Monza     = 14
#   Abu Dhabi = 22
#
# 2022
#   Suzuka    = 18
#

YEAR = 2022
ROUND = 18
SESSION = "R"

DRIVER = "VER"
LAP = 1


def print_distribution(distribution):

    print("=" * 120)
    print("DISTRIBUTION")
    print("=" * 120)

    print(
        f"Full Throttle : {distribution['fullThrottle']:.2f}%"
    )
    print(
        f"Partial       : {distribution['partialThrottle']:.2f}%"
    )
    print(
        f"Brake         : {distribution['brake']:.2f}%"
    )
    print(
        f"Rolling       : {distribution['rolling']:.2f}%"
    )
    print(
        f"Lift & Coast  : {distribution['liftAndCoast']:.2f}%"
    )
    print(
        f"Cornering     : {distribution['cornering']:.2f}%"
    )
    print(
        f"Clipping      : {distribution['clipping']:.2f}%"
    )

    print()


def print_clipping(events):

    print("=" * 120)
    print("CLIPPING EVENTS")
    print("=" * 120)

    if not events:

        print("None\n")
        return

    for index, event in enumerate(events, start=1):

        corners = [
            f"{corner['number']}{corner['letter']}"
            for corner in event["zone"]["corners"]
        ]

        print("-" * 120)

        print(
            f"#{index:02d} "
            f"{event['classification']:16} "
            f"Score={event['score']}"
        )

        print(
            f"Corners={corners}"
        )

        print(
            f"{event['firstRelationship']} -> "
            f"{event['lastRelationship']}"
        )

        print(
            f"{event['startTime']:.3f}s -> "
            f"{event['endTime']:.3f}s"
            f" ({event['duration']:.3f}s)"
        )

        print(
            f"Speed "
            f"{event['startSpeed']:.0f}"
            f"→"
            f"{event['endSpeed']:.0f}"
            f"  Max={event['maximumSpeed']:.0f}"
        )

        print(
            f"Speed Ratio = {event['speedRatio']:.3f}"
        )

        print(
            f"Accel Ratio = {event['accelerationRatio']:.3f}"
        )

        print(
            "Reasons : "
            + (
                ", ".join(event["reasons"])
                if event["reasons"]
                else "None"
            )
        )

    print()


def print_lift_coast(events):

    print("=" * 120)
    print("OFF THROTTLE EVENTS")
    print("=" * 120)

    if not events:

        print("None\n")
        return

    for index, event in enumerate(events, start=1):

        corners = [
            f"{corner['number']}{corner['letter']}"
            for corner in event["zone"]["corners"]
        ]

        print("-" * 120)

        print(
            f"#{index:02d} "
            f"{event['classification']:18} "
            f"Score={event['score']}"
        )

        print(
            f"Corners={corners}"
        )

        print(
            f"{event['firstRelationship']} -> "
            f"{event['lastRelationship']}"
        )

        print(
            f"{event['startTime']:.3f}s -> "
            f"{event['endTime']:.3f}s"
            f" ({event['duration']:.3f}s)"
        )

        print(
            f"Speed "
            f"{event['startSpeed']:.0f}"
            f"→"
            f"{event['endSpeed']:.0f}"
            f" Loss={event['speedLoss']:.0f}"
        )

        print(
            f"Speed Loss Ratio = "
            f"{event['speedLossRatio']:.3f}"
        )

        print(
            f"RPM Loss Ratio   = "
            f"{event['rpmLossRatio']:.3f}"
        )

        print(
            f"Duration Ratio   = "
            f"{event['durationRatio']:.3f}"
        )

        print(
            f"Distance Ratio   = "
            f"{event['distanceRatio']:.3f}"
        )

        print(
            "Reasons : "
            + (
                ", ".join(event["reasons"])
                if event["reasons"]
                else "None"
            )
        )

    print()


def print_phases(phases):

    print("=" * 120)
    print("DRIVING PHASES")
    print("=" * 120)

    for phase in phases:

        print(
            f"{phase['startTime']:8.3f}"
            f" - "
            f"{phase['endTime']:8.3f}"
            f" | "
            f"{phase['phase']:5}"
            f" | "
            f"{phase['duration']:6.3f}s"
        )

    print()


def main():

    fastf1.Cache.enable_cache(CACHE_DIR)

    session = fastf1.get_session(
        YEAR,
        ROUND,
        SESSION,
    )

    session.load()

    lap = (
        session.laps
        .pick_drivers(DRIVER)
        .pick_laps(LAP)
        .iloc[0]
    )

    telemetry = (
        lap
        .get_car_data()
        .add_distance()
    )

    analysis = LapAnalysisBuilder.build(
        telemetry,
        session,
    )

    print()

    print_distribution(
        analysis["distribution"]
    )

    print_clipping(
        analysis["clippingEvents"]
    )

    print_lift_coast(
        analysis["liftCoastEvents"]
    )

    print_phases(
        analysis["phases"]
    )


if __name__ == "__main__":
    main()