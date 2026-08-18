import math
from typing import Literal
import pandas as pd

from app.services.session_cache_service import (
    get_loaded_qualifying_session
)

from app.services.team_normalizer import normalize_team_name

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
        to the driver's official fastest lap in Q1/Q2/Q3.
        """

        session = get_loaded_qualifying_session(
            year,
            round_number
        )

        driver = driver.upper()

        result = session.results.loc[
            session.results["Abbreviation"] == driver
        ]

        if result.empty:
            raise ValueError(
                f"Driver '{driver}' not found"
            )

        result_row = result.iloc[0]

        target_lap_time = result_row[session_part]

        if pd.isna(target_lap_time):
            raise ValueError(
                f"{driver} has no {session_part} time"
            )

        driver_laps = (
            session.laps
            .pick_drivers(driver)
            .dropna(subset=["LapTime"])
            .copy()
        )

        if driver_laps.empty:
            raise ValueError(
                f"Unable to locate any laps for {driver}"
            )

        #
        # Compare lap times using a small tolerance instead
        # of exact Timedelta equality.
        #
        tolerance = pd.Timedelta(milliseconds=2)

        matching_laps = driver_laps.loc[
            (
                driver_laps["LapTime"] - target_lap_time
            ).abs() <= tolerance
        ]

        if matching_laps.empty:

            #
            # Fallback:
            # Select the driver's fastest valid lap.
            #
            fastest_lap_index = (
                driver_laps["LapTime"].idxmin()
            )

            fastest_lap = driver_laps.loc[
                fastest_lap_index
            ]

            #
            # Make sure the fallback lap is actually close
            # to the official session result.
            #
            if (
                abs(
                    fastest_lap["LapTime"]
                    - target_lap_time
                )
                > tolerance
            ):
                raise ValueError(
                    f"Unable to locate {session_part} lap "
                    f"for {driver}. "
                    f"Official time: {target_lap_time}, "
                    f"closest lap: {fastest_lap['LapTime']}"
                )

            return fastest_lap

        #
        # Normally there should only be one matching lap.
        #
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
        
    def get_session_fastest_sectors(
        self,
        year: int,
        round_number: int,
        session_part: SessionPart,
    ):
        session = get_loaded_qualifying_session(
            year,
            round_number,
        )

        #
        # Drivers who set an official time in this session
        #
        results = session.results.loc[
            session.results[session_part].notna()
        ]

        fastest = {
            "Sector1Time": None,
            "Sector2Time": None,
            "Sector3Time": None,
        }

        for _, result in results.iterrows():

            lap = self.get_fastest_lap(
                year,
                round_number,
                result["Abbreviation"],
                session_part,
            )

            for sector in fastest:

                current = lap[sector]

                if current is None:
                    continue

                if (
                    fastest[sector] is None
                    or current < fastest[sector]
                ):
                    fastest[sector] = current

        return fastest

    def build_driver_payload(
        self,
        year: int,
        round_number: int,
        driver: str,
        session_part: SessionPart,
        session_fastest_sectors,
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
        
        driver_info = session.get_driver(driver.upper())
        
        
        
        normalized_team_name = normalize_team_name(
            result_row["TeamName"]
        )

        start_row = telemetry.iloc[0]
        end_row = telemetry.iloc[-1]

        return {
            "driver": driver.upper(),
            
            "driverName": driver_info["LastName"],

            "teamName": normalized_team_name,

            "teamColor": result_row["TeamColor"],

            "position": int(
                result_row["Position"]
            ),

            "lapNumber": int(
                lap["LapNumber"]
            ),

            "driverNumber": str(
                lap["DriverNumber"]
            ),

            "compound": (
                str(lap["Compound"]).upper()
                if lap["Compound"] is not None
                else None
            ),

            "tyreAge": (
                int(lap["TyreLife"])
                if lap["TyreLife"] is not None
                else None
            ),

            "freshTyre": (
                bool(lap["FreshTyre"])
                if lap["FreshTyre"] is not None
                else None
            ),

            "stint": (
                int(lap["Stint"])
                if lap["Stint"] is not None
                else None
            ),

            "lapTime": round(
                lap["LapTime"].total_seconds(),
                3
            ),

            "sector1": round(
                lap["Sector1Time"].total_seconds(),
                3
            ),

            "isSector1SessionFastest": (
                lap["Sector1Time"]
                == session_fastest_sectors["Sector1Time"]
            ),

            "sector2": round(
                lap["Sector2Time"].total_seconds(),
                3
            ),

            "isSector2SessionFastest": (
                lap["Sector2Time"]
                == session_fastest_sectors["Sector2Time"]
            ),

            "sector3": round(
                lap["Sector3Time"].total_seconds(),
                3
            ),

            "isSector3SessionFastest": (
                lap["Sector3Time"]
                == session_fastest_sectors["Sector3Time"]
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
        
        session_fastest_sectors = self.get_session_fastest_sectors(
            year,
            round_number,
            session_part,
        )

        driver_a_payload = (
            self.build_driver_payload(
                year,
                round_number,
                driver_a,
                session_part,
                session_fastest_sectors,
            )
        )

        driver_b_payload = None

        if driver_b:

            driver_b_payload = (
                self.build_driver_payload(
                    year,
                    round_number,
                    driver_b,
                    session_part,
                    session_fastest_sectors,
                )
            )
            
        session = get_loaded_qualifying_session(
            year,
            round_number
        )

        return {
            "year": year,

            "grandPrix": session.event["EventName"],
            
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

        times = telemetry["Time"].dt.total_seconds().to_numpy()
        distances = telemetry["Distance"].to_numpy()

        sector_markers = []

        for sector_name, sector_time in [
            ("S1", sector1_end),
            ("S2", sector2_end),
        ]:

            #
            # Find the first telemetry sample after the sector time
            #
            after_index = next(
                (
                    i
                    for i, t in enumerate(times)
                    if t >= sector_time
                ),
                len(times) - 1,
            )

            before_index = max(0, after_index - 1)

            t1 = times[before_index]
            t2 = times[after_index]

            d1 = distances[before_index]
            d2 = distances[after_index]

            #
            # Linear interpolation
            #
            if t2 == t1:
                distance = d1
            else:
                ratio = (sector_time - t1) / (t2 - t1)
                distance = d1 + ratio * (d2 - d1)

            sector_markers.append({
                "sector": sector_name,
                "time": round(sector_time, 3),
                "rd": round(distance / max_distance, 5),
                "d": round(distance, 2),
            })

        return sector_markers