# File: backend/src/cruds/briefing.py

from sqlalchemy.orm import Session
from typing import List, Optional # Importar Optional
from datetime import datetime # Para usar datetime.now() para update_date

from src.models.briefing import Briefing
from src.schemas.briefing import BriefingCreate, BriefingUpdate
# from src.utils.datetime_utils import get_current_datetime_brasilia # Remover se não for mais usada aqui

def get_briefing(db: Session, briefing_id: int) -> Optional[Briefing]:
    return db.query(Briefing).filter(Briefing.id == briefing_id).first()

def get_briefings_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Briefing]:
    return db.query(Briefing).filter(Briefing.user_id == user_id).offset(skip).limit(limit).all()

def get_briefings(db: Session, skip: int = 0, limit: int = 100) -> List[Briefing]:
    return db.query(Briefing).offset(skip).limit(limit).all()

def create_briefing(db: Session, briefing: BriefingCreate) -> Briefing:
    db_briefing = Briefing(
        user_id=briefing.user_id,
        # CORRIGIDO: Mapear para os campos existentes no modelo Briefing
        title=briefing.title,
        content=briefing.content, # JSON content
        status=briefing.status,
        development_roteiro=briefing.development_roteiro, # JSON, pode ser None
        last_edited_by=briefing.last_edited_by, # Pode ser None
        # REMOVIDOS: project_name, project_description, target_audience, goals,
        # content_pages, design_preferences, technical_requirements - Não existem no modelo Briefing.
        # REMOVIDOS: created_at - O modelo Briefing tem 'creation_date' com server_default=CURRENT_TIMESTAMP.
        # REMOVIDOS: updated_at - O modelo Briefing tem 'update_date' que é gerenciado na atualização.
    )
    db.add(db_briefing)
    db.commit()
    db.refresh(db_briefing)
    return db_briefing

def update_briefing(db: Session, briefing_id: int, briefing: BriefingUpdate) -> Optional[Briefing]:
    db_briefing = db.query(Briefing).filter(Briefing.id == briefing_id).first()
    if db_briefing:
        for key, value in briefing.dict(exclude_unset=True).items():
            # Apenas atribui o valor se o campo existir no modelo Briefing
            if hasattr(db_briefing, key):
                setattr(db_briefing, key, value)
            # REMOVIDO: Lógica para campos que não existem mais no modelo (ex: project_name, etc.)
        
        # CORRIGIDO: Usar 'update_date' em vez de 'updated_at'
        db_briefing.update_date = datetime.now() # Ou get_current_datetime_brasilia() se for mantido
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