import fastf1

from app.config.settings import settings


def init_fastf1_cache():
    fastf1.Cache.enable_cache(
        settings.FASTF1_CACHE_DIR
    )