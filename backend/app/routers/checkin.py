from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.checkin import CheckinCreate, CheckinResponse
from app.services.checkin import create_checkin, get_today_checkin

router = APIRouter()

# MVP: user_id fijo hasta tener auth. Reemplazar con dependency de auth.
MVP_USER_ID = 1


@router.post("", response_model=CheckinResponse, status_code=201)
async def create_checkin_endpoint(
    payload: CheckinCreate,
    db: Session = Depends(get_db),
) -> CheckinResponse:
    try:
        return await create_checkin(db, MVP_USER_ID, payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/today", response_model=CheckinResponse | None)
def get_today_checkin_endpoint(db: Session = Depends(get_db)) -> CheckinResponse | None:
    return get_today_checkin(db, MVP_USER_ID)
