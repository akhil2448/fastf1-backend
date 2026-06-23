import fastf1
from threading import Lock

session_cache = {}

session_load_lock = Lock()


def get_loaded_session(year: int, round_number: int):
    """
    Returns cached loaded FastF1 race session.
    Prevents concurrent duplicate loads.
    """

    cache_key = (year, round_number)

    # Fast path
    if cache_key in session_cache:
        return session_cache[cache_key]

    # Only ONE thread may load
    with session_load_lock:

        # Recheck after acquiring lock
        if cache_key in session_cache:
            return session_cache[cache_key]

        session = fastf1.get_session(
            year,
            round_number,
            "R"
        )

        session.load(
            laps=True,
            telemetry=True,
            weather=True,
            messages=True
        )

        session_cache[cache_key] = session

        return session
    
    
    qualifying_session_cache = {}
    
    def get_loaded_qualifying_session(
        year: int,
        round_number: int
    ):
        """
        Returns cached loaded FastF1 qualifying session.
        """

        cache_key = (
            year,
            round_number,
            "Q"
        )

        if cache_key in qualifying_session_cache:
            return qualifying_session_cache[cache_key]

        with session_load_lock:

            if cache_key in qualifying_session_cache:
                return qualifying_session_cache[cache_key]

            session = fastf1.get_session(
                year,
                round_number,
                "Q"
            )

            session.load(
                laps=True,
                telemetry=True,
                weather=False,
                messages=False
            )

            qualifying_session_cache[cache_key] = session

            return session