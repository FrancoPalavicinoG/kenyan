from fastapi import FastAPI

from app.config import settings
from app.routers import sync, user

app = FastAPI(title="Kenyan API")

app.include_router(sync.router, prefix="/sync", tags=["sync"])
app.include_router(user.router, prefix="/users", tags=["users"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "kenyan is alive ;)", "environment": settings.ENVIRONMENT}
