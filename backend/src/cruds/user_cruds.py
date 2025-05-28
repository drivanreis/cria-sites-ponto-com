# File: backend/src/cruds/user.py

from sqlalchemy.orm import Session
from typing import List, Optional
from src.models.user_models import User
from src.schemas.user_schemas import UserCreate, UserUpdate
from src.utils.datetime_utils import get_current_datetime_str
from src.core.security import get_password_hash, verify_password
from fastapi import HTTPException, status # Importar para levantar HTTPExceptions
from sqlalchemy.exc import IntegrityError # Importar para tratar erros de integridade

# --- Funções CRUD ---

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_phone_number(db: Session, phone_number: str) -> Optional[User]:
    return db.query(User).filter(User.phone_number == phone_number).first()

def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    return db.query(User).filter(User.google_id == google_id).first()

def get_user_by_github_id(db: Session, github_id: str) -> Optional[User]:
    return db.query(User).filter(User.github_id == github_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

# Função para criar um novo usuário
def create_user(db: Session, user: UserCreate) -> User:
    # As verificações de email e phone_number duplicados já estão no router,
    # mas é bom ter um fallback aqui para IntegrityError.

    hashed_password = None
    if user.password:
        hashed_password = get_password_hash(user.password)
    
    current_datetime_str = get_current_datetime_str()

    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        phone_number=user.phone_number,
        creation_date=current_datetime_str,
        last_login=None
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        # Este bloco captura erros de unicidade que podem ter passado
        # pela verificação inicial (ex: em concorrência)
        error_message = str(e)
        if "Duplicate entry" in error_message:
            if "email" in error_message:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já registrado")
            elif "phone_number" in error_message:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Número de telefone já registrado")
            # Adicione outras verificações de campos únicos se houver
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Dados duplicados. Verifique os campos únicos.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor ao criar usuário.")


# Função para atualizar um usuário existente
def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        update_data = user.model_dump(exclude_unset=True) 
        
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            db_user.password_hash = hashed_password
            del update_data["password"]
        
        for key, value in update_data.items():
            if hasattr(db_user, key):
                setattr(db_user, key, value)
        
        try: # Adicionar try-except para IntegrityError em updates também
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            db.rollback()
            error_message = str(e)
            if "Duplicate entry" in error_message:
                if "email" in error_message:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já registrado")
                elif "phone_number" in error_message:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Número de telefone já registrado")
                else:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Dados duplicados. Verifique os campos únicos.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor ao atualizar usuário.")
    return db_user

# Função para deletar um usuário
def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False