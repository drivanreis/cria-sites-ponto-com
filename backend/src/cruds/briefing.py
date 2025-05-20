# File: backend/src/cruds/briefing.py

from sqlalchemy.orm import Session
from typing import List

from src.models.briefing import Briefing
from src.schemas.briefing import BriefingCreate, BriefingUpdate
from src.utils.datetime_utils import get_current_datetime_brasilia

def get_briefing(db: Session, briefing_id: int):
    return db.query(Briefing).filter(Briefing.id == briefing_id).first()

def get_briefings_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Briefing]:
    return db.query(Briefing).filter(Briefing.user_id == user_id).offset(skip).limit(limit).all()

def get_briefings(db: Session, skip: int = 0, limit: int = 100) -> List[Briefing]:
    return db.query(Briefing).offset(skip).limit(limit).all()

def create_briefing(db: Session, briefing: BriefingCreate) -> Briefing:
    db_briefing = Briefing(
        user_id=briefing.user_id,
        project_name=briefing.project_name,
        project_description=briefing.project_description,
        target_audience=briefing.target_audience,
        goals=briefing.goals,
        content_pages=briefing.content_pages,
        design_preferences=briefing.design_preferences,
        technical_requirements=briefing.technical_requirements,
        status=briefing.status,
        created_at=get_current_datetime_brasilia(),
        updated_at=get_current_datetime_brasilia()
    )
    db.add(db_briefing)
    db.commit()
    db.refresh(db_briefing)
    return db_briefing

def update_briefing(db: Session, briefing_id: int, briefing: BriefingUpdate) -> Briefing | None:
    db_briefing = db.query(Briefing).filter(Briefing.id == briefing_id).first()
    if db_briefing:
        for key, value in briefing.dict(exclude_unset=True).items():
            setattr(db_briefing, key, value)
        
        db_briefing.updated_at = get_current_datetime_brasilia()
        db.commit()
        db.refresh(db_briefing)
    return db_briefing

def delete_briefing(db: Session, briefing_id: int) -> bool:
    db_briefing = db.query(Briefing).filter(Briefing.id == briefing_id).first()
    if db_briefing:
        db.delete(db_briefing)
        db.commit()
        return True
    return False