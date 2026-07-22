
##  FOR FETCHING TEAMCOLORS FROM RACE SESSIONS IF QUALIFYING SESSIONS HAVE EMPTY VALUES

class TeamMetadataService:

    def get_race_team_colors(
        self,
        race_session,
    ):

        return (
            race_session.results
            .set_index("DriverNumber")["TeamColor"]
            .to_dict()
        )

    def get_team_color(
        self,
        quali_row,
        race_team_colors
    ):
        color = (
            quali_row["TeamColor"] or ""
        ).strip()

        if color:
            return color

        return race_team_colors.get(
            quali_row["DriverNumber"],
            ""
        )