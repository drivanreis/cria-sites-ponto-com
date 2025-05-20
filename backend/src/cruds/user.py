# File: backend/src/cruds/user.py

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.utils.datetime_utils import get_current_datetime_brasilia
import bcrypt # For password hashing

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    # Hash the password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    db_user = User(
        full_name=user.full_name,
        email=user.email,
        # Store the hashed password
        password=hashed_password.decode('utf-8'), 
        phone_number=user.phone_number,
        company_name=user.company_name,
        role=user.role,
        is_active=user.is_active,
        created_at=get_current_datetime_brasilia(),
        updated_at=get_current_datetime_brasilia()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: UserUpdate) -> User | None:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        for key, value in user.dict(exclude_unset=True).items():
            if key == "password" and value:
                # Hash new password if provided
                hashed_password = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt())
                setattr(db_user, key, hashed_password.decode('utf-8'))
            else:
                setattr(db_user, key, value)
        
        db_user.updated_at = get_current_datetime_brasilia() # Update timestamp
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# Function to verify password (for authentication purposes later)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))