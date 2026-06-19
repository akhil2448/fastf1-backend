import fastf1
import pandas as pd


def format_lap_time(td):
    """
    Convert pandas Timedelta to:
    1:13.447
    """

    if pd.isna(td):
        return None

    total_seconds = td.total_seconds()

    minutes = int(total_seconds // 60)

    seconds = total_seconds % 60

    return f"{minutes}:{seconds:06.3f}"


def generate_qualifying_results(
    year: int,
    round_number: int
) -> dict:

    # =====================================
    # Load Qualifying Session
    # =====================================

    quali_session = fastf1.get_session(
        year,
        round_number,
        "Q"
    )

    quali_session.load()

    # =====================================
    # Load Race Session
    # =====================================

    race_session = fastf1.get_session(
        year,
        round_number,
        "R"
    )

    race_session.load()

    # =====================================
    # Grid Positions
    # =====================================

    grid_positions = (
        race_session.results
        .set_index("DriverNumber")
        ["GridPosition"]
        .to_dict()
    )

    results = []

    # =====================================
    # Build Driver Results
    # =====================================

    for _, row in quali_session.results.iterrows():

        q1_td = row["Q1"]
        q2_td = row["Q2"]
        q3_td = row["Q3"]

        q1 = format_lap_time(q1_td)
        q2 = format_lap_time(q2_td)
        q3 = format_lap_time(q3_td)

        # -------------------------------
        # Determine final qualifying round
        # -------------------------------

        if pd.notna(q3_td):

            final_session = "Q3"
            final_lap_time = q3
            raw_final_time = q3_td

        elif pd.notna(q2_td):

            final_session = "Q2"
            final_lap_time = q2
            raw_final_time = q2_td

        else:

            final_session = "Q1"
            final_lap_time = q1
            raw_final_time = q1_td

        grid_position = grid_positions.get(
            row["DriverNumber"]
        )

        results.append({
            "position": int(row["Position"]),

            "driverNumber": row["DriverNumber"],

            "abbreviation": row["Abbreviation"],

            "driverId": row["DriverId"],

            "lastName": row["LastName"],

            "teamName": row["TeamName"],

            "teamColor": row["TeamColor"],

            "headshotUrl": row["HeadshotUrl"],

            "gridPosition":
                int(grid_position)
                if pd.notna(grid_position)
                else None,

            "q1": q1,
            "q2": q2,
            "q3": q3,

            "finalSession": final_session,

            "finalLapTime": final_lap_time,

            "_rawFinalTime": raw_final_time
        })

    # =====================================
    # Convert Q3 Times To Intervals
    # =====================================

    q3_results = [
        driver
        for driver in results
        if driver["finalSession"] == "Q3"
    ]

    q3_results.sort(
        key=lambda driver: driver["position"]
    )

    for index, driver in enumerate(q3_results):

        # Pole sitter keeps lap time

        if index == 0:
            continue

        current_time = driver["_rawFinalTime"]

        previous_time = q3_results[
            index - 1
        ][
            "_rawFinalTime"
        ]

        if pd.isna(current_time) or pd.isna(previous_time):

            driver["finalLapTime"] = None

            continue

        gap_seconds = (
            current_time - previous_time
        ).total_seconds()

        driver["finalLapTime"] = (
            f"+{gap_seconds:.3f}"
        )

    # =====================================
    # Remove Helper Field
    # =====================================

    for driver in results:

        driver.pop(
            "_rawFinalTime",
            None
        )

    return {
        "session": {
            "year": year,
            "round": round_number,
            "raceName": quali_session.event["EventName"]
        },
        "qualifyingResults": results
    }