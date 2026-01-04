def build_weather_json(weather_df, session, calendar_date):
    weather_df = weather_df.where(weather_df.notna(), None)

    weather_json = {
        "session": {
            "year": calendar_date.year,
            "Date": f"{calendar_date.month}/{calendar_date.day}",
            "event": session.event["EventName"],
            "location": session.event["Location"],
            "type": "Race"
        },
        "weatherData": []
    }

    for _, row in weather_df.iterrows():
        weather_json["weatherData"].append({
            "Time": row["Time"],
            "AirTemp": row["AirTemp"],
            "Humidity": row["Humidity"],
            "Pressure": row["Pressure"],
            "Rainfall": row["Rainfall"],
            "TrackTemp": row["TrackTemp"],
            "WindDirection": row["WindDirection"],
            "WindSpeed": row["WindSpeed"]
        })

    return weather_json
