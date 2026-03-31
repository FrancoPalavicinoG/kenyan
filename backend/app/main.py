from fastapi import FastAPI

from app.config import settings

app = FastAPI(title="Kenyan API")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "alive ;)", "environment": settings.ENVIRONMENT}
