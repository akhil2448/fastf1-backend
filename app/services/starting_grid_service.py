from app.services.race_service import _safe_int
from app.services.session_cache_service import get_loaded_session
from app.services.team_normalizer import normalize_team_name
from app.services.race_management.tyre_compound_service import TyreCompoundService


class StartingGridService:

    def __init__(self):
        self.tyre_service = TyreCompoundService()

    def get_starting_grid(
        self,
        year: int,
        round_number: int,
    ):
        """
        Returns the official starting grid together with the tyre
        compound used to start the race.
        """

        session = get_loaded_session(
            year,
            round_number,
        )

        #
        # Base grid information
        #
        grid = session.results[
            [
                "GridPosition",
                "Abbreviation",
                "DriverNumber",
                "FullName",
                "TeamName",
                "TeamColor",
            ]
        ].copy()

        #
        # Remove invalid / DNS entries
        #
        grid = grid[
            grid["GridPosition"].notna()
        ]

        grid = grid[
            grid["GridPosition"] > 0
        ]

        #
        # Normalize team names
        #
        grid["TeamName"] = grid["TeamName"].apply(
            normalize_team_name
        )

        #
        # Tyres used on Lap 1
        #
        lap_one = session.laps[
            session.laps["LapNumber"] == 1
        ][
            [
                "DriverNumber",
                "Compound",
                "FreshTyre",
                "TyreLife"
            ]
        ].copy()

        #
        # Normalize compounds
        #
        lap_one["Compound"] = lap_one["Compound"].apply(
            self.tyre_service.normalize
        )

        #
        # Merge tyre information
        #
        grid = grid.merge(
            lap_one,
            on="DriverNumber",
            how="left",
        )

        #
        # Pole → last
        #
        grid = grid.sort_values(
            by="GridPosition"
        ).reset_index(drop=True)

        #
        # Serialize
        #
        return [
            {
                "position": int(row.GridPosition),
                "driver": row.Abbreviation,
                "driverNumber": str(row.DriverNumber),
                "fullName": row.FullName,
                "team": row.TeamName,
                # "teamColor": row.TeamColor,
                "compound": row.Compound,
                "freshTyre": (
                    bool(row.FreshTyre)
                    if row.FreshTyre is not None
                    else None
                ),
                "tyreLife": (
                    max(0, _safe_int(row.TyreLife) - 1)
                    if _safe_int(row.TyreLife) is not None
                    else None
                )
            }
            for row in grid.itertuples(index=False)
        ]