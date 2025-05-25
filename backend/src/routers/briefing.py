# File: backend/src/routers/briefing.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from src.cruds import briefing as crud_briefing
from src.schemas.briefing import BriefingCreate, BriefingUpdate, BriefingInDB
from src.db.database import get_db

# CORRIGIDO: Adicionado prefix e tags para organização da API
router = APIRouter(
    prefix="/briefings",
    tags=["Briefings"]
)

@router.post("/", response_model=BriefingInDB, status_code=status.HTTP_201_CREATED)
def create_new_briefing(briefing: BriefingCreate, db: Session = Depends(get_db)):
    # Basic check for existing briefing (e.g., by user_id and title)
    # If you later decide to enforce unique titles per user, you'd add:
    # db_briefing = crud_briefing.get_briefing_by_user_id_and_title(db, user_id=briefing.user_id, title=briefing.title)
    # if db_briefing:
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Briefing with this title already exists for this user")
    return crud_briefing.create_briefing(db=db, briefing=briefing)

@router.get("/", response_model=List[BriefingInDB])
def read_briefings(
    user_id: Optional[int] = None, # Optional filter by user_id
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    if user_id:
        briefings = crud_briefing.get_briefings_by_user(db, user_id=user_id, skip=skip, limit=limit)
    else:
        briefings = crud_briefing.get_briefings(db, skip=skip, limit=limit)
    return briefings

@router.get("/{briefing_id}", response_model=BriefingInDB)
def read_briefing(briefing_id: int, db: Session = Depends(get_db)):
    db_briefing = crud_briefing.get_briefing(db, briefing_id=briefing_id)
    if db_briefing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Briefing not found")
    return db_briefing

@router.put("/{briefing_id}", response_model=BriefingInDB)
def update_existing_briefing(briefing_id: int, briefing: BriefingUpdate, db: Session = Depends(get_db)):
    db_briefing = crud_briefing.update_briefing(db, briefing_id=briefing_id, briefing=briefing)
    if db_briefing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Briefing not found")
    return db_briefing

@router.delete("/{briefing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_briefing(briefing_id: int, db: Session = Depends(get_db)):
    success = crud_briefing.delete_briefing(db, briefing_id=briefing_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Briefing not found")
    # CORRIGIDO: Para 204 No Content, o corpo da resposta deve ser vazio.
    return