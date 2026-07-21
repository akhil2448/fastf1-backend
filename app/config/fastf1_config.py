# import fastf1

# def init_fastf1_cache(cache_dir="cache"):
#     fastf1.Cache.enable_cache(cache_dir)


import os
import fastf1

def init_fastf1_cache():
    cache_dir = os.getenv("FASTF1_CACHE_DIR", "cache")
    fastf1.Cache.enable_cache(cache_dir)