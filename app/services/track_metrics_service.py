import pandas as pd


TARGET_TIMING_LOOPS = 60


def build_track_metrics(session):
    """
    Single authoritative track metrics source.
    """

    session.load(laps=True, telemetry=True)

    fastest_lap = session.laps.pick_fastest()

    tel = fastest_lap.get_telemetry().copy()
    tel = tel.add_distance()
    tel = tel.sort_values("Distance")

    tel["LapDistance"] = (
        tel["Distance"] - tel["Distance"].min()
    )

    track_length = float(
        tel["LapDistance"].max()
    )

    timing_loop_count = TARGET_TIMING_LOOPS

    timing_loop_spacing = (
        track_length / timing_loop_count
    )

    return {
        "trackLength": round(track_length, 3),

        "timingLoopCount": timing_loop_count,

        "timingLoopSpacing": round(
            timing_loop_spacing,
            3
        )
    }