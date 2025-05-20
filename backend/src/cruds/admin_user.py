# File: backend/src/cruds/admin_user.py

from sqlalchemy.orm import Session
from typing import List

from src.models.admin_user import AdminUser
from src.schemas.admin_user import AdminUserCreate, AdminUserUpdate
from src.utils.datetime_utils import get_current_datetime_brasilia
import bcrypt

def get_admin_user(db: Session, admin_user_id: int):
    return db.query(AdminUser).filter(AdminUser.id == admin_user_id).first()

def get_admin_user_by_email(db: Session, email: str):
    return db.query(AdminUser).filter(AdminUser.email == email).first()

def get_admin_users(db: Session, skip: int = 0, limit: int = 100) -> List[AdminUser]:
    return db.query(AdminUser).offset(skip).limit(limit).all()

def create_admin_user(db: Session, admin_user: AdminUserCreate) -> AdminUser:
    hashed_password = bcrypt.hashpw(admin_user.password.encode('utf-8'), bcrypt.gensalt())
    
    db_admin_user = AdminUser(
        full_name=admin_user.full_name,
        email=admin_user.email,
        password=hashed_password.decode('utf-8'),
        is_active=admin_user.is_active,
        is_super_admin=admin_user.is_super_admin,
        created_at=get_current_datetime_brasilia(),
        updated_at=get_current_datetime_brasilia()
    )
    db.add(db_admin_user)
    db.commit()
    db.refresh(db_admin_user)
    return db_admin_user

def update_admin_user(db: Session, admin_user_id: int, admin_user: AdminUserUpdate) -> AdminUser | None:
    db_admin_user = db.query(AdminUser).filter(AdminUser.id == admin_user_id).first()
    if db_admin_user:
        for key, value in admin_user.dict(exclude_unset=True).items():
            if key == "password" and value:
                hashed_password = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt())
                setattr(db_admin_user, key, hashed_password.decode('utf-8'))
            else:
                setattr(db_admin_user, key, value)
        
        db_admin_user.updated_at = get_current_datetime_brasilia()
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

# Re-using the verify_password from user CRUDS (or move to a common utils/auth.py if needed)
# from src.cruds.user import verify_password
# Note: For now, I'm assuming verify_password is in user.py.
# If you prefer, we can create a common authentication utility.