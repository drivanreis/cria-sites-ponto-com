# File: backend/src/core/security.py

from datetime import datetime, timedelta, timezone # Necessário para cálculos de data/hora
from typing import Optional, Union
import logging # Adicionado para logging

from jose import jwt, JWTError
from passlib.context import CryptContext # Para hashing de senhas
from sqlalchemy.orm import Session # Para a função authenticate_user

from src.core.config import settings
from src.schemas.token_schemas import TokenData # O esquema TokenData (id, username, user_type)
from src.models.admin_user_models import AdminUser # Modelo de AdminUser
from src.models.user_models import User # Modelo de User comum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    """Cria um token de acesso JWT. Usa o tempo de expiração padrão para o tipo de usuário ou um tempo delta customizado."""
    to_encode = data.copy()
    
    # Define a expiração com base no user_type ou expires_delta
    if expires_delta:
        expire_dt = datetime.now(timezone.utc) + expires_delta
    else:
        # Padrão: usa as configurações globais de expiração
        user_type = data.get("user_type", "user") # Padrão para 'user' se não especificado
        if user_type == "admin":
            expire_dt = datetime.now(timezone.utc) + timedelta(minutes=settings.ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES)
        else: # user comum
            expire_dt = datetime.now(timezone.utc) + timedelta(minutes=settings.USER_ACCESS_TOKEN_EXPIRE_MINUTES)
            
    to_encode.update({"exp": expire_dt})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decodifica um token JWT e retorna os dados essenciais (id, username, user_type)."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Validar e extrair os dados essenciais
        user_id: Optional[int] = payload.get("id")
        username: Optional[str] = payload.get("username") # Este é o identificador de login (username do admin, email/telefone do user)
        user_type: Optional[str] = payload.get("user_type")

        if user_id is None or username is None or user_type is None:
            logger.warning(f"Token JWT com dados essenciais faltando: {payload}")
            return None # Dados essenciais faltando no token

        # >>> CORREÇÃO/MELHORIA: Popular o campo 'email' do TokenData apenas para user_type='user' se for um email <<<
        email_for_token_data = None
        if user_type == "user" and "@" in username:
            email_for_token_data = username
        elif user_type == "user" and not "@" in username:
            # Se for user mas não tem @, pode ser telefone. Email fica None.
            pass
        
        return TokenData(id=user_id, username=username, email=email_for_token_data, user_type=user_type)
    except JWTError as e:
        logger.error(f"Erro na decodificação do token JWT: {e}")
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
        logger.info(f"AdminUser '{identifier}' autenticado com sucesso.")
        return admin_user

    # 2. Se não for AdminUser, tenta autenticar como User usando o 'identifier' como email
    user_by_email = db.query(User).filter(User.email == identifier).first()
    if user_by_email and verify_password(password, user_by_email.password_hash):
        logger.info(f"User com email '{identifier}' autenticado com sucesso.")
        return user_by_email

    # 3. Se não for User por email, tenta autenticar como User usando o 'identifier' como phone_number
    user_by_phone = db.query(User).filter(User.phone_number == identifier).first()
    if user_by_phone and verify_password(password, user_by_phone.password_hash):
        logger.info(f"User com telefone '{identifier}' autenticado com sucesso.")
        return user_by_phone
    
    logger.warning(f"Falha na autenticação para o identificador: '{identifier}'")
    return None