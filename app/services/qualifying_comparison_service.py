import math
from typing import Literal

from app.services.session_cache_service import (
    get_loaded_qualifying_session
)

SessionPart = Literal["Q1", "Q2", "Q3"]


class QualifyingComparisonService:

    def get_fastest_lap(
        self,
        year: int,
        round_number: int,
        driver: str,
        session_part: SessionPart
    ):
        """
        Returns the FastF1 Lap object corresponding
        to the driver's fastest lap in Q1/Q2/Q3.
        """

        session = get_loaded_qualifying_session(
            year,
            round_number
        )

        result = session.results.loc[
            session.results["Abbreviation"] == driver.upper()
        ]

        if result.empty:
            raise ValueError(
                f"Driver '{driver}' not found"
            )

        result_row = result.iloc[0]

        target_lap_time = result_row[session_part]

        if target_lap_time is None:
            raise ValueError(
                f"{driver} has no {session_part} time"
            )

        driver_laps = (
            session.laps
            .pick_drivers(driver.upper())
        )

        matching_laps = driver_laps.loc[
            driver_laps["LapTime"] == target_lap_time
        ]

        if matching_laps.empty:
            raise ValueError(
                f"Unable to locate {session_part} lap for {driver}"
            )

        return matching_laps.iloc[0]

    def build_track_map(
        self,
        year: int,
        round_number: int
    ):
        """
        Returns:
        - Closed track polyline
        - Track bounds
        - Start/finish line
        """

        session = get_loaded_qualifying_session(
            year,
            round_number
        )

        reference_lap = session.laps.pick_fastest()
        
        circuit_info = session.get_circuit_info()
        corners = circuit_info.corners

        telemetry = reference_lap.get_telemetry()
        
        max_distance = float(telemetry["Distance"].max())

        sector_markers = self.build_sector_markers(
            reference_lap,
            max_distance
        )

        sector1_rd = sector_markers[0]["rd"]
        sector2_rd = sector_markers[1]["rd"]

        points = []

        sector1 = []
        sector2 = []
        sector3 = []
        
        corner_markers = []

        xs = []
        ys = []

        for _, row in telemetry.iterrows():

            x = row["X"]
            y = row["Y"]

            if x is None or y is None:
                continue

            x = round(float(x), 2)
            y = round(float(y), 2)

            rd = float(row["Distance"]) / max_distance

            point = {
                "x": x,
                "y": y
            }

            points.append(point)

            #
            # Build colored sectors
            #

            if rd <= sector1_rd:

                if not sector1:
                    sector1.append(point)

                sector1.append(point)

            elif rd <= sector2_rd:

                if not sector2:
                    sector2.append(point)

                sector2.append(point)

            else:

                if not sector3:
                    sector3.append(point)

                sector3.append(point)

            xs.append(x)
            ys.append(y)

        if len(points) < 2:
            raise ValueError(
                "Unable to build track map."
            )

        #
        # Close sector polylines
        #

        if sector1 and sector2:
            sector1.append(sector2[0])

        if sector2 and sector3:
            sector2.append(sector3[0])

        if sector3 and sector1:
            sector3.append(sector1[0])

        #
        # Keep the full track closed
        #

        points.append(points[0])

        bounds = {
            "minX": round(min(xs), 2),
            "maxX": round(max(xs), 2),
            "minY": round(min(ys), 2),
            "maxY": round(max(ys), 2)
        }

        # --------------------------
        # START / FINISH LINE
        # --------------------------

        start_point = points[0]
        second_point = points[1]

        dx = (
            second_point["x"]
            - start_point["x"]
        )

        dy = (
            second_point["y"]
            - start_point["y"]
        )

        length = math.sqrt(
            dx * dx +
            dy * dy
        )

        if length == 0:
            length = 1

        dx /= length
        dy /= length

        px = -dy
        py = dx

        line_half_width = 80

        start_finish = {
            "x1": round(
                start_point["x"] + px * line_half_width,
                2
            ),
            "y1": round(
                start_point["y"] + py * line_half_width,
                2
            ),
            "x2": round(
                start_point["x"] - px * line_half_width,
                2
            ),
            "y2": round(
                start_point["y"] - py * line_half_width,
                2
            )
        }

        width = round(
            bounds["maxX"] - bounds["minX"],
            2
        )

        height = round(
            bounds["maxY"] - bounds["minY"],
            2
        )
        
        #
        # Corner markers
        #

        for _, row in corners.iterrows():

            corner_markers.append({
                "number": int(row["Number"]),
                "x": round(float(row["X"]), 2),
                "y": round(float(row["Y"]), 2),
                "angle": round(float(row["Angle"]), 2),
                "distance": round(float(row["Distance"]), 2),
            })

        return {
            "sector1": sector1,
            "sector2": sector2,
            "sector3": sector3,
            
            "corners": corner_markers,

            "bounds": bounds,

            "width": width,

            "height": height,

            "startPoint": {
                "x": start_point["x"],
                "y": start_point["y"]
            },

            "startFinish": start_finish
        }

    def build_driver_payload(
        self,
        year: int,
        round_number: int,
        driver: str,
        session_part: SessionPart
    ):
        """
        Returns telemetry payload for
        driver's fastest qualifying lap.
        """

        session = get_loaded_qualifying_session(
            year,
            round_number
        )

        lap = self.get_fastest_lap(
            year,
            round_number,
            driver,
            session_part
        )

        telemetry = lap.get_telemetry()

        max_distance = float(
            telemetry["Distance"].max()
        )
        
        sector_markers = self.build_sector_markers(
            lap,
            max_distance
        )

        telemetry_rows = []

        for idx, (_, row) in enumerate(
            telemetry.iterrows()
        ):

            normalized_rd = (
                float(row["Distance"]) / max_distance
                if max_distance > 0
                else 0
            )

            telemetry_rows.append({
                "idx": idx,

                "rd": round(
                    normalized_rd,
                    5
                ),

                "t": round(
                    row["Time"].total_seconds(),
                    3
                ),

                "d": round(
                    float(row["Distance"]),
                    2
                ),

                "speed": int(
                    row["Speed"]
                ),

                "rpm": int(
                    row["RPM"]
                ),

                "throttle": round(
                    float(row["Throttle"]),
                    1
                ),

                "brake": 100 if bool(row["Brake"]) else 0,

                "gear": int(
                    row["nGear"]
                ),

                "x": round(
                    float(row["X"]),
                    2
                ),

                "y": round(
                    float(row["Y"]),
                    2
                )
            })
        
        

        result_row = (
            session.results
            .loc[
                session.results["Abbreviation"]
                == driver.upper()
            ]
            .iloc[0]
        )

        start_row = telemetry.iloc[0]
        end_row = telemetry.iloc[-1]

        return {
            "driver": driver.upper(),

            "teamName": result_row["TeamName"],

            "teamColor": result_row["TeamColor"],

            "position": int(
                result_row["Position"]
            ),

            "lapNumber": int(
                lap["LapNumber"]
            ),

            "lapTime": round(
                lap["LapTime"].total_seconds(),
                3
            ),

            "sector1": round(
                lap["Sector1Time"].total_seconds(),
                3
            ),

            "sector2": round(
                lap["Sector2Time"].total_seconds(),
                3
            ),

            "sector3": round(
                lap["Sector3Time"].total_seconds(),
                3
            ),
            
            "sectorMarkers": sector_markers,

            "sampleCount": len(
                telemetry_rows
            ),

            "maxDistance": round(
                max_distance,
                2
            ),

            "startPoint": {
                "x": round(
                    float(start_row["X"]),
                    2
                ),
                "y": round(
                    float(start_row["Y"]),
                    2
                )
            },

            "endPoint": {
                "x": round(
                    float(end_row["X"]),
                    2
                ),
                "y": round(
                    float(end_row["Y"]),
                    2
                )
            },

            "telemetry": telemetry_rows
        }
        
        
    def build_comparison_payload(
        self,
        year: int,
        round_number: int,
        session_part: SessionPart,
        driver_a: str,
        driver_b: str | None = None
    ):

        driver_a_payload = (
            self.build_driver_payload(
                year,
                round_number,
                driver_a,
                session_part
            )
        )

        driver_b_payload = None

        if driver_b:

            driver_b_payload = (
                self.build_driver_payload(
                    year,
                    round_number,
                    driver_b,
                    session_part
                )
            )

        return {
            "sessionPart": session_part,

            "trackMap": self.build_track_map(
                year,
                round_number
            ),

            "driverA": driver_a_payload,

            "driverB": driver_b_payload
        }
        
    def build_sector_markers(
        self,
        lap,
        max_distance: float
    ):
        """
        Returns sector boundaries as relative distance.

        Example:
        S1 end = 0.26
        S2 end = 0.69
        """

        telemetry = lap.get_telemetry()

        sector1_end = (
            lap["Sector1Time"].total_seconds()
        )

        sector2_end = (
            sector1_end +
            lap["Sector2Time"].total_seconds()
        )

        sector_markers = []

        for sector_name, sector_time in [
            ("S1", sector1_end),
            ("S2", sector2_end)
        ]:

            nearest_row = telemetry.loc[
                (
                    telemetry["Time"]
                    .dt.total_seconds()
                    .sub(sector_time)
                    .abs()
                ).idxmin()
            ]

            rd = (
                float(nearest_row["Distance"])
                / max_distance
            )

            sector_markers.append({
                "sector": sector_name,
                "time": round(
                    sector_time,
                    3
                ),
                "rd": round(
                    rd,
                    5
                )
            })

        return sector_markers