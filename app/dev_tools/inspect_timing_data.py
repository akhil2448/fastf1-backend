from app.services.session_cache_service import get_loaded_session

YEAR = 2024
ROUND = 11


def main():

    session = get_loaded_session(
        YEAR,
        ROUND,
    )

    print()

    print("=" * 100)
    print("SESSION ATTRIBUTES")
    print("=" * 100)

    attrs = [
        a
        for a in dir(session)
        if not a.startswith("_")
    ]

    for attr in sorted(attrs):

        try:

            value = getattr(
                session,
                attr
            )

            print(
                f"{attr:<35}"
                f"{type(value)}"
            )

        except Exception:

            pass


if __name__ == "__main__":
    main()