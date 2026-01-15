import numpy as np
import json


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
    telemetry = lap.get_telemetry()[["X", "Y", "Distance"]]
    telemetry = telemetry.sort_values("Distance")

    # Track length (meters)
    track_length = float(telemetry["Distance"].max())

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
            "trackLength": round(track_length, 2)  # meters
        },
        "coordinates": coordinates
    }

    # Optional save to file
    if save_to_file:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(track_json, f, indent=2, ensure_ascii=False)

    return track_json
