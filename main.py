from fastapi import FastAPI
from app.api.routes import router
from app.config.fastf1_config import init_fastf1_cache

from fastapi.middleware.cors import CORSMiddleware

from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI(title="FastF1 Race Data API")

init_fastf1_cache()

app.add_middleware(
    GZipMiddleware,
    minimum_size=1024  # compress responses > 1 KB
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)