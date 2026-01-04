import fastf1

def init_fastf1_cache(cache_dir="cache"):
    fastf1.Cache.enable_cache(cache_dir)