from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.sync import SyncResult
from app.services.garmin import run_backfill, run_daily_sync

router = APIRouter()

# MVP: single user. Replace with auth dependency when ready.
USER_ID = 1


@router.post("/trigger", response_model=SyncResult)
def trigger_sync(db: Session = Depends(get_db)) -> SyncResult:
    return run_daily_sync(db, USER_ID)


@router.post("/backfill", response_model=SyncResult)
def backfill_sync(
    days: int = Query(default=90, ge=1, le=365),
    db: Session = Depends(get_db),
) -> SyncResult:
    return run_backfill(db, USER_ID, days)
