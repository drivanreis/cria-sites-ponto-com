# File: backend/src/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from typing import Optional

from src.db.database import get_db
from src.cruds import admin_user as crud_admin_user
from src.schemas.token import Token
from src.core.config import settings
from jose import jwt
from src.utils.datetime_utils import get_current_datetime_str

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # >>> CORREÇÃO: Usar o padrão para USUÁRIOS COMUNS se não especificado <<<
        # Em rotas de login específicas, como a de admin, passaremos expires_delta explicitamente.
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.USER_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Rota de Login para AdminUser
@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    admin_user = crud_admin_user.get_admin_user_by_username(db, username=form_data.username)

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not crud_admin_user.verify_password(form_data.password, admin_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # >>> CORREÇÃO: Usar ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES aqui <<<
    access_token_expires = timedelta(minutes=settings.ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"id": admin_user.id, "username": admin_user.username, "user_type": "admin"},
        expires_delta=access_token_expires
    )

    admin_user.last_login = get_current_datetime_str()
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    return {"access_token": access_token, "token_type": "bearer"}