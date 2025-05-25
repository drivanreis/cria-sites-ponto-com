# File: backend/src/cruds/admin_user.py

from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.context import CryptContext 
from src.models.admin_user import AdminUser
from src.schemas.admin_user import AdminUserCreate, AdminUserUpdate
from src.utils.datetime_utils import get_current_datetime_str

# Para hashear e verificar senhas (usando bcrypt como esquema)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funções CRUD ---

def get_admin_user(db: Session, admin_user_id: int) -> Optional[AdminUser]:
    return db.query(AdminUser).filter(AdminUser.id == admin_user_id).first()

def get_admin_user_by_username(db: Session, username: str) -> Optional[AdminUser]:
    return db.query(AdminUser).filter(AdminUser.username == username).first()

def get_admin_users(db: Session, skip: int = 0, limit: int = 100) -> List[AdminUser]:
    return db.query(AdminUser).offset(skip).limit(limit).all()

def create_admin_user(db: Session, admin_user: AdminUserCreate) -> AdminUser:
    hashed_password = pwd_context.hash(admin_user.password)
    current_datetime_str = get_current_datetime_str()

    db_admin_user = AdminUser(
        username=admin_user.username,
        password_hash=hashed_password,
        creation_date=current_datetime_str,
        last_login=None
        # two_factor_secret e is_two_factor_enabled serão inicializados com None e False
        # pelos seus defaults no modelo AdminUser.
    )
    db.add(db_admin_user)
    db.commit()
    db.refresh(db_admin_user)
    return db_admin_user

def update_admin_user(db: Session, admin_user_id: int, admin_user: AdminUserUpdate) -> Optional[AdminUser]:
    db_admin_user = db.query(AdminUser).filter(AdminUser.id == admin_user_id).first()
    if db_admin_user:
        update_data = admin_user.model_dump(exclude_unset=True) 
        
        if "password" in update_data and update_data["password"]:
            hashed_password = pwd_context.hash(update_data["password"])
            db_admin_user.password_hash = hashed_password
            del update_data["password"]
        
        for key, value in update_data.items():
            if hasattr(db_admin_user, key):
                setattr(db_admin_user, key, value)
        
        db.add(db_admin_user)
        db.commit()
        db.refresh(db_admin_user)
    return db_admin_user

def delete_admin_user(db: Session, admin_user_id: int) -> bool:
    db_admin_user = db.query(AdminUser).filter(AdminUser.id == admin_user_id).first()
    if db_admin_user:
        db.delete(db_admin_user)
        db.commit()
        return True
    return False

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)