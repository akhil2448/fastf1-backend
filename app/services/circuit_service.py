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
      "trackInfo": { ... },
      "coordinates": [ {x, y, isStart?}, ... ]
    }
    """

    # Load required data
    session.load(laps=True, telemetry=True)

    # Use fastest lap for clean racing line
    lap = session.laps.pick_fastest()
    telemetry = lap.get_telemetry()[["X", "Y", "Distance"]]
    telemetry = telemetry.sort_values("Distance")

    # Rotate track using circuit info
    circuit_info = session.get_circuit_info()
    angle = np.deg2rad(circuit_info.rotation)

    rotation_matrix = np.array([
        [np.cos(angle),  np.sin(angle)],
        [-np.sin(angle), np.cos(angle)]
    ])

    rotated = telemetry[["X", "Y"]].to_numpy().dot(rotation_matrix)

    # Build coordinates array
    coordinates = []
    for idx, (x, y) in enumerate(rotated):
        point = {
            "x": float(x),
            "y": float(y)
        }
        if include_start_point and idx == 0:
            point["isStart"] = True
        coordinates.append(point)

    # Build final JSON
    track_json = {
        "trackInfo": {
            "eventName": session.event["EventName"],
            "location": session.event["Location"],
            "country": session.event["Country"],
            "officialEventName": session.event["OfficialEventName"]
        },
        "coordinates": coordinates
    }

    # Optional save to file
    if save_to_file:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(track_json, f, indent=2, ensure_ascii=False)

    return track_json