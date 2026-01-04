import numpy as np
import json

def generate_track_map(session, include_start_point=True,
                       save_to_file=False, filename="track_map.json"):

    session.load(laps=True, telemetry=True)

    lap = session.laps.pick_fastest()
    telemetry = lap.get_telemetry()[["X", "Y", "Distance"]]
    telemetry = telemetry.sort_values("Distance")

    angle = np.deg2rad(session.get_circuit_info().rotation)

    rotation_matrix = np.array([
        [np.cos(angle), np.sin(angle)],
        [-np.sin(angle), np.cos(angle)]
    ])

    rotated = telemetry[["X", "Y"]].to_numpy().dot(rotation_matrix)

    track_map = []
    for idx, (x, y) in enumerate(rotated):
        point = {"x": float(x), "y": float(y)}
        if include_start_point and idx == 0:
            point["isStart"] = True
        track_map.append(point)

    if save_to_file:
        with open(filename, "w") as f:
            json.dump(track_map, f, indent=2)

    return track_map
