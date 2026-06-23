from app.services.session_cache_service import (
    get_loaded_qualifying_session
)


def get_qualifying_session_summary(
    year: int,
    round_number: int
):
    """
    Temporary method.
    Used only to inspect available FastF1 data.
    """

    session = get_loaded_qualifying_session(
        year,
        round_number
    )

    return {
        "event": session.event["EventName"],
        "lapsCount": len(session.laps),
        "driversCount": len(session.results)
    }