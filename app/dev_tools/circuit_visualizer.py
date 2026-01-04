import matplotlib.pyplot as plt

def visualize_track_map(track_map, title="Track Map"):
    """
    Visualizes a track map and highlights the start point.
    Intended for local debugging only.
    """

    x = [p["x"] for p in track_map]
    y = [p["y"] for p in track_map]

    start_point = next((p for p in track_map if p.get("isStart")), None)

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
    plt.title(title)

    if start_point:
        plt.legend()

    plt.show()
