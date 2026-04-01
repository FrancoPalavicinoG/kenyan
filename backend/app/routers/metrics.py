from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.metrics import TodayMetrics
from app.services.metrics import get_today_metrics

router = APIRouter()

# MVP: user_id fijo hasta tener auth. Reemplazar con dependency de auth.
MVP_USER_ID = 1


@router.get("/today", response_model=TodayMetrics)
def get_today_metrics_endpoint(db: Session = Depends(get_db)) -> TodayMetrics:
    return get_today_metrics(db, MVP_USER_ID)
