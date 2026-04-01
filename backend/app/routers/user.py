from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user import create_user, get_user, update_user

router = APIRouter()

# MVP: user_id fijo hasta tener auth. Reemplazar con dependency de auth.
MVP_USER_ID = 1


@router.post("", response_model=UserResponse, status_code=201)
def create_user_endpoint(payload: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    try:
        return create_user(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=UserResponse)
def get_current_user(db: Session = Depends(get_db)) -> UserResponse:
    try:
        return get_user(db, MVP_USER_ID)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/me", response_model=UserResponse)
def update_current_user(payload: UserUpdate, db: Session = Depends(get_db)) -> UserResponse:
    try:
        return update_user(db, MVP_USER_ID, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
