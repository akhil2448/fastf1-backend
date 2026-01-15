def generate_race_json(laps, session, calendar_date):
    race_json = {
        "session": {
            "year": calendar_date.year,
            "Date": f"{calendar_date.month}/{calendar_date.day}",
            "event": session.event["EventName"],
            "location": session.event["Location"],
            "type": "Race",
            "totalLaps": session.total_laps
        },
        "drivers": {}
    }

    lap_columns = [
        "LapNumber",
        "LapTime",
        "Time",
        "LapStartTime",
        "Position",
        "TyreLife"
    ]

    # Group by Driver + DriverNumber to avoid key collisions
    for (driver, driver_number), df in laps.groupby(["Driver", "DriverNumber"]):
        df = df.where(df.notna(), None).sort_values("LapNumber")

        driver_block = {
            "DriverNumber": driver_number,
            "Team": df.iloc[0]["Team"],
            "laps": [],
            "PitStopData": [],
            "PersonalBestLaps": []
        }

        for _, row in df.iterrows():
            lap_number = row["LapNumber"]

            # -------- laps[] --------
            driver_block["laps"].append(
                {col: row[col] for col in lap_columns}
            )

            # -------- PitStopData[] --------
            if lap_number == 1 or row["PitInTime"] or row["PitOutTime"]:
                driver_block["PitStopData"].append({
                    "LapNumber": lap_number,
                    "PitInTime": row["PitInTime"],
                    "PitOutTime": row["PitOutTime"],
                    "Compound": row["Compound"]
                })

            # -------- PersonalBestLaps[] --------
            if row["IsPersonalBest"] is True:
                driver_block["PersonalBestLaps"].append(lap_number)

        race_json["drivers"][driver] = driver_block

    return race_json
