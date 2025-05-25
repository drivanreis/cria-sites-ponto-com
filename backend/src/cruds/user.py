# File: src/cruds/user.py

from sqlalchemy.orm import Session
from typing import List, Optional
# Removido: from passlib.context import CryptContext (movido para security.py)
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.utils.datetime_utils import get_current_datetime_str

# >>> NOVIDADE/CORREÇÃO: Importar get_password_hash e verify_password do módulo de segurança <<<
from src.core.security import get_password_hash, verify_password

# Removido: pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") (movido para security.py)

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
    hashed_password = None
    if user.password: # Apenas hashear se a senha for fornecida (para login local)
        # >>> CORREÇÃO: Usar get_password_hash do módulo de segurança <<<
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
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Função para atualizar um usuário existente
def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        update_data = user.model_dump(exclude_unset=True) 
        
        if "password" in update_data and update_data["password"]:
            # >>> CORREÇÃO: Usar get_password_hash do módulo de segurança <<<
            hashed_password = get_password_hash(update_data["password"])
            db_user.password_hash = hashed_password
            del update_data["password"]
        
        for key, value in update_data.items():
            if hasattr(db_user, key):
                setattr(db_user, key, value)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return db_user

# Função para deletar um usuário
def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# Removido: def verify_password(plain_password: str, hashed_password: str) -> bool: (movido para security.py)