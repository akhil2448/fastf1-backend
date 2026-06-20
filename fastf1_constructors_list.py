import fastf1

fastf1.Cache.enable_cache("cache")


def get_unique_team_names(start_year=2018, end_year=2025):
    """
    Returns all unique TeamName values found in FastF1 session results.
    """

    team_names = set()

    for year in range(start_year, end_year + 1):
        schedule = fastf1.get_event_schedule(year)

        for _, event in schedule.iterrows():
            try:
                session = fastf1.get_session(
                    year,
                    event["EventName"],
                    "R"  # Race session
                )

                session.load(
                    laps=False,
                    telemetry=False,
                    weather=False,
                    messages=False
                )

                if session.results is not None:
                    teams = (
                        session.results["TeamName"]
                        .dropna()
                        .unique()
                    )

                    team_names.update(teams)

            except Exception as e:
                print(f"Failed: {year} - {event['EventName']} - {e}")

    return sorted(team_names)


teams = get_unique_team_names()

print(f"Found {len(teams)} unique team names:")
for team in teams:
    print(team)