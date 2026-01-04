def build_track_status_json(track_status_df, session, calendar_date):
    track_status_df = track_status_df.where(track_status_df.notna(), None)

    track_status_json = {
        "session": {
            "year": calendar_date.year,
            "Date": f"{calendar_date.month}/{calendar_date.day}",
            "event": session.event["EventName"],
            "location": session.event["Location"],
            "type": "Race"
        },
        "trackStatusData": []
    }

    for _, row in track_status_df.iterrows():
        track_status_json["trackStatusData"].append({
            "Time": row["Time"],
            "TrackStatus": int(row["TrackStatus"])
        })

    return track_status_json
