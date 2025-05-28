# File: src/core/security.py

from datetime import datetime, timedelta, timezone # Necessário para cálculos de data/hora
from typing import Optional, Union

from jose import jwt, JWTError
from passlib.context import CryptContext # Para hashing de senhas
from sqlalchemy.orm import Session # Para a função authenticate_user

from src.core.config import settings
from src.schemas.token_schemas import TokenData # O esquema TokenData (id, username, user_type)
from src.models.admin_user_models import AdminUser # Modelo de AdminUser
from src.models.user_models import User # Modelo de User comum

# Contexto para hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Utilitários de Senha ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano corresponde ao hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera o hash de uma senha."""
    return pwd_context.hash(password)

# --- Utilitários de Token JWT ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token de acesso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire_dt = datetime.now(timezone.utc) + expires_delta
    else:
        # Padrão para USUÁRIOS COMUNS se não especificado
        expire_dt = datetime.now(timezone.utc) + timedelta(minutes=settings.USER_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire_dt.timestamp()}) # Adiciona o timestamp de expiração
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenData]:
    """Decodifica um token de acesso JWT e retorna os dados."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        id: int = payload.get("id")
        username: str = payload.get("username") # Pode ser username do admin ou email/telefone do user
        user_type: str = payload.get("user_type")

        if id is None or username is None or user_type is None:
            return None # Dados essenciais faltando no token

        return TokenData(id=id, username=username, user_type=user_type)
    except JWTError:
        return None # Erro na decodificação do token

# --- Lógica de Autenticação Unificada ---
def authenticate_user(db: Session, identifier: str, password: str) -> Optional[Union[AdminUser, User]]:
    """
    Tenta autenticar um usuário (AdminUser ou User comum) usando um identificador
    (username para admin, email para user ou phone_number para user) e senha.
    """
    # 1. Tenta autenticar como AdminUser usando o 'identifier' como username
    admin_user = db.query(AdminUser).filter(AdminUser.username == identifier).first()
    if admin_user and verify_password(password, admin_user.password_hash):
        return admin_user

    # 2. Se não for AdminUser, tenta autenticar como User usando o 'identifier' como email
    user_by_email = db.query(User).filter(User.email == identifier).first()
    if user_by_email and verify_password(password, user_by_email.password_hash):
        return user_by_email

    # 3. Se não for User por email, tenta autenticar como User usando o 'identifier' como phone_number
    user_by_phone = db.query(User).filter(User.phone_number == identifier).first()
    if user_by_phone and verify_password(password, user_by_phone.password_hash):
        return user_by_phone

    return None # Nenhuma credencial correspondeu