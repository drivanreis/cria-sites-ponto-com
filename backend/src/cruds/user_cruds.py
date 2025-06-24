# File: backend/src/cruds/user_cruds.py

from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import logging

from src.models.user_models import User
from src.schemas.user_schemas import UserCreate, UserUpdate
from src.utils.datetime_utils import get_current_datetime_str
from src.core.security import get_password_hash, verify_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Funções CRUD ---

def get_user(db: Session, user_id: int) -> Optional[User]:
    logger.info(f"Buscando usuário com ID: {user_id}")
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    logger.info(f"Buscando usuário com email: '{email}'")
    return db.query(User).filter(User.email == email).first()

def get_user_by_phone_number(db: Session, phone_number: str) -> Optional[User]:
    logger.info(f"Buscando usuário com telefone: '{phone_number}'")
    return db.query(User).filter(User.phone_number == phone_number).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    logger.info(f"Buscando lista de usuários (skip={skip}, limit={limit})")
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    logger.info("Iniciando criação de novo usuário")
    
    # Verifica duplicidade apenas se email ou telefone forem informados
    if user.email and get_user_by_email(db, user.email):
        raise HTTPException(status_code=409, detail="Email já registrado por outro usuário.")
    if user.phone_number and get_user_by_phone_number(db, user.phone_number):
        raise HTTPException(status_code=409, detail="Número de telefone já registrado por outro usuário.")

    hashed_password = get_password_hash(user.password) if user.password else None

    db_user = User(
        nickname=user.nickname,
        email=user.email,
        phone_number=user.phone_number,
        password_hash=hashed_password,
        google_id=user.google_id,
        github_id=user.github_id,
        creation_date=get_current_datetime_str()
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Usuário criado com sucesso. ID: {db_user.id}")
        return db_user
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Erro de integridade ao criar usuário: {e}")
        raise HTTPException(status_code=409, detail="Conflito de dados únicos.")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro inesperado ao criar usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao criar usuário.")

def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    logger.info(f"Tentando atualizar usuário ID: {user_id}")
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        logger.warning(f"Usuário ID {user_id} não encontrado.")
        return None

    update_data = user.model_dump(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(db_user, key, value)

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Usuário ID {user_id} atualizado com sucesso.")
        return db_user
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Erro de integridade ao atualizar usuário ID {user_id}: {e}")
        raise HTTPException(status_code=409, detail="Conflito de dados únicos na atualização.")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro inesperado ao atualizar usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar usuário.")

def delete_user(db: Session, user_id: int) -> bool:
    logger.info(f"Tentando deletar usuário ID: {user_id}")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        logger.warning(f"Usuário ID {user_id} não encontrado para deleção.")
        return False

    try:
        db.delete(db_user)
        db.commit()
        logger.info(f"Usuário ID {user_id} deletado com sucesso.")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao deletar usuário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao deletar usuário.")

def get_user_by_identifier(db: Session, identifier: str) -> Optional[User]:
    user = get_user_by_email(db, identifier)
    if user:
        return user
    user = get_user_by_phone_number(db, identifier)
    return user

def verify_user_password(db: Session, user_id: int, plain_password: str) -> bool:
    db_user = get_user(db, user_id)
    if db_user and db_user.password_hash:
        return verify_password(plain_password, db_user.password_hash)
    return False
