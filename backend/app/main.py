from fastapi import FastAPI

from app.config import settings
from app.routers import sync

app = FastAPI(title="Kenyan API")

app.include_router(sync.router, prefix="/sync", tags=["sync"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "alive ;)", "environment": settings.ENVIRONMENT}
