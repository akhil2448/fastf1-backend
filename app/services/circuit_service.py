import numpy as np
import json

from app.services.track_metrics_service import build_track_metrics

def generate_track_map(
    session,
    include_start_point=True,
    save_to_file=False,
    filename="track_map.json"
):
    """
    Generates track map JSON with track metadata and coordinates.

    Output structure:
    {
      "trackInfo": {
          "eventName": ...,
          "location": ...,
          "country": ...,
          "officialEventName": ...,
          "trackLength": <meters>
      },
      "coordinates": [ {x, y, isStart?}, ..., {x, y, isFinish?} ]
    }
    """

    # Load required data
    session.load(laps=True, telemetry=True)

    # Use fastest lap for clean racing line
    lap = session.laps.pick_fastest()
    
    telemetry = lap.get_telemetry().copy()
    telemetry = telemetry.add_distance()
    telemetry = telemetry.sort_values("Distance")

    # Lap-relative distance (even for fastest lap)
    telemetry["LapDistance"] = (
        telemetry["Distance"] - telemetry["Distance"].min()
    )

    # Robust track length (meters)
    track_metrics = build_track_metrics(session)
    track_length = track_metrics["trackLength"]


    # Rotate track using circuit info
    circuit_info = session.get_circuit_info()
    angle = np.deg2rad(circuit_info.rotation)

    rotation_matrix = np.array([
        [np.cos(angle),  np.sin(angle)],
        [-np.sin(angle), np.cos(angle)]
    ])

    rotated = telemetry[["X", "Y"]].to_numpy().dot(rotation_matrix)

    # ---- Center the track ----
    xs = rotated[:, 0]
    ys = rotated[:, 1]

    center_x = (xs.max() + xs.min()) / 2
    center_y = (ys.max() + ys.min()) / 2

    rotated[:, 0] -= center_x
    rotated[:, 1] -= center_y

    # ---- Build coordinates array ----
    coordinates = []

    for idx, (x, y) in enumerate(rotated):
        point = {
            "x": float(x),
            "y": float(y)
        }
        if include_start_point and idx == 0:
            point["isStart"] = True

        coordinates.append(point)

    # ---- Close the track loop ----
    if coordinates:
        coordinates.append({
            "x": coordinates[0]["x"],
            "y": coordinates[0]["y"],
            "isFinish": True
        })

    # ---- Final JSON ----
    track_json = {
        "trackInfo": {
            "eventName": session.event["EventName"],
            "location": session.event["Location"],
            "country": session.event["Country"],
            "officialEventName": session.event["OfficialEventName"],

            "trackLength": round(track_length, 2),

            "timingLoopCount":
                track_metrics["timingLoopCount"],

            "timingLoopSpacing":
                track_metrics["timingLoopSpacing"],
        },
        "coordinates": coordinates
    }

    # Optional save to file
    if save_to_file:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(track_json, f, indent=2, ensure_ascii=False)

    return track_json
