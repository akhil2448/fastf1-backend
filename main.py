from fastapi import FastAPI
from app.api.routes import router
from app.config.fastf1_config import init_fastf1_cache

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config.settings import settings

app = FastAPI(title="FastF1 Race Data API")

init_fastf1_cache()

app.add_middleware(
    GZipMiddleware,
    minimum_size=1024
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------
# Root endpoint
# -----------------------
@app.get("/", tags=["System"])
def root():
    return {
        "name": "PitWall API",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


# -----------------------
# Health check
# -----------------------
@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
    }


app.include_router(router)