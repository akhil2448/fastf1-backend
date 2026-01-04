from fastapi import FastAPI
from app.api.routes import router
from app.config.fastf1_config import init_fastf1_cache

app = FastAPI(title="FastF1 Race Data API")

init_fastf1_cache()
app.include_router(router)
