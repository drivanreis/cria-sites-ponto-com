# File: backend/src/cruds/briefing_cruds.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import logging
from fastapi import HTTPException, status

from src.models.briefing_models import Briefing
from src.schemas.briefing_schemas import BriefingCreate, BriefingUpdate
from src.utils.datetime_utils import get_current_datetime_str

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Funções CRUD para Briefing ---

def get_briefing(db: Session, briefing_id: int) -> Optional[Briefing]:
    """
    Busca um briefing pelo seu ID.
    """
    logger.info(f"Buscando briefing com ID: {briefing_id}")
    return db.query(Briefing).filter(Briefing.id == briefing_id).first()

def get_briefings_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Briefing]:
    """
    Retorna uma lista de briefings de um usuário específico, com paginação.
    """
    logger.info(f"Buscando briefings para o usuário ID: {user_id}")
    return db.query(Briefing).filter(Briefing.user_id == user_id).offset(skip).limit(limit).all()

def get_briefing_by_user_id_and_title(db: Session, user_id: int, title: str) -> Optional[Briefing]:
    """
    Busca um briefing pelo user_id e título.
    Útil para conversas contínuas onde o título é gerado com base no employee_name.
    """
    logger.info(f"Buscando briefing para user_id '{user_id}' com título '{title}'")
    return db.query(Briefing).filter(Briefing.user_id == user_id, Briefing.title == title).first()

def create_briefing(db: Session, briefing: BriefingCreate, user_id: int) -> Briefing:
    """
    Cria um novo registro de briefing no banco de dados.
    """
    logger.info(f"Tentando criar novo briefing para user_id: {user_id} com título: '{briefing.title}'")
    db_briefing = Briefing(
        **briefing.model_dump(),
        user_id=user_id,
        creation_date=get_current_datetime_str(),
        last_edited_by="user" # Assumimos que o usuário cria o briefing inicialmente
    )
    try:
        db.add(db_briefing)
        db.commit()
        db.refresh(db_briefing)
        logger.info(f"Briefing ID {db_briefing.id} criado com sucesso para user_id: {user_id}.")
        return db_briefing
    except IntegrityError as e:
        db.rollback()
        error_message = str(e.orig)
        logger.error(f"Erro de integridade ao criar briefing: {error_message}")
        if "_user_title_uc" in error_message: # Nome do UniqueConstraint definido no modelo
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um briefing com este título para este usuário."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar briefing: {error_message}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Erro inesperado ao criar briefing para user_id {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor ao criar briefing: {e}"
        )

def update_briefing(db: Session, briefing_id: int, briefing: BriefingUpdate, editor_type: str = "user") -> Optional[Briefing]:
    """
    Atualiza um registro de briefing existente.
    Permite que 'editor_type' seja 'user' ou 'admin' ou 'ai'.
    """
    logger.info(f"Tentando atualizar briefing ID: {briefing_id} por {editor_type}")
    db_briefing = db.query(Briefing).filter(Briefing.id == briefing_id).first()
    if not db_briefing:
        logger.warning(f"Briefing ID {briefing_id} não encontrado para atualização.")
        return None

    update_data = briefing.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_briefing, key, value)
    
    db_briefing.update_date = get_current_datetime_str()
    db_briefing.last_edited_by = editor_type

    try:
        db.add(db_briefing)
        db.commit()
        db.refresh(db_briefing)
        logger.info(f"Briefing ID {briefing_id} atualizado com sucesso por {editor_type}.")
        return db_briefing
    except IntegrityError as e:
        db.rollback()
        error_message = str(e.orig)
        logger.error(f"Erro de integridade ao atualizar briefing ID {briefing_id}: {error_message}")
        if "_user_title_uc" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe outro briefing com este título para o mesmo usuário."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar briefing: {error_message}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Erro inesperado ao atualizar briefing ID {briefing_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor ao atualizar briefing: {e}"
        )

def delete_briefing(db: Session, briefing_id: int) -> bool:
    """
    Deleta um registro de briefing.
    """
    logger.info(f"Tentando deletar briefing ID: {briefing_id}")
    db_briefing = db.query(Briefing).filter(Briefing.id == briefing_id).first()
    if db_briefing:
        try:
            db.delete(db_briefing)
            db.commit()
            logger.info(f"Briefing ID {briefing_id} deletado com sucesso.")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Erro inesperado ao deletar briefing ID {briefing_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno do servidor ao deletar briefing: {e}"
            )
    logger.warning(f"Briefing ID {briefing_id} não encontrado para deleção.")
    return False