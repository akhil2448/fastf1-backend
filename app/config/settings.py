from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    ENV = os.getenv("ENV", "development")

    # FastF1 cache location.
    # Local: defaults to ./cache
    # Docker/Production: set FASTF1_CACHE_DIR explicitly,
    # e.g. /app/cache (container-mounted persistent cache).
    FASTF1_CACHE_DIR = os.getenv(
        "FASTF1_CACHE_DIR",
        "cache"
    )

    # Frontend URL allowed by CORS.
    # Local: http://localhost:4200
    # Production: set FRONTEND_URL to the deployed frontend URL.
    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "http://localhost:4200"
    )

    LOG_LEVEL = os.getenv(
        "LOG_LEVEL",
        "INFO"
    )


settings = Settings()