import matplotlib.pyplot as plt

def visualize_track_map(track_json):
    """
    Visualizes a track map and highlights the start point.
    Intended for local debugging only.
    """

    coordinates = track_json["coordinates"]
    track_info = track_json.get("trackInfo", {})

    x = [p["x"] for p in coordinates]
    y = [p["y"] for p in coordinates]

    start_point = next((p for p in coordinates if p.get("isStart")), None)

    # Build a meaningful title
    title_parts = [
        track_info.get("eventName"),
        track_info.get("location"),
        track_info.get("country")
    ]
    title = " – ".join(filter(None, title_parts))

    plt.figure(figsize=(10, 8))
    plt.plot(x, y, color="black", linewidth=2)

    if start_point:
        plt.scatter(
            start_point["x"],
            start_point["y"],
            color="red",
            s=120,
            zorder=5,
            label="Start / Finish"
        )

    plt.axis("equal")
    plt.axis("off")
    plt.title(title if title else "Track Map")

    if start_point:
        plt.legend()

    plt.show()
