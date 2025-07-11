# File: backend/src/dependencies/oauth_file.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional, Union
import logging

from src.core.config import settings
from src.schemas.token_schemas import TokenData
from src.db.database import get_db
from src.models.admin_user_models import AdminUser
from src.models.user_models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def decode_access_token(token: str) -> TokenData:
    """
    Decodifica um token JWT e valida seu payload.
    Retorna uma instância de TokenData.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        token_id: int = payload.get("id")
        token_username: str = payload.get("username")
        token_user_type: str = payload.get("user_type")
        token_email: Optional[str] = payload.get("email")

        if token_id is None or token_username is None or token_user_type is None:
            raise credentials_exception
        
        return TokenData(id=token_id, username=token_username, user_type=token_user_type, email=token_email)
    
    except JWTError as e:
        logger.warning(f"Erro de JWT ao decodificar token: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Erro inesperado ao decodificar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor ao processar token."
        )


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> TokenData: # <--- IMPORTANTE: Altere o tipo de retorno para TokenData
    """
    Dependência que valida o token, decodifica-o e busca o usuário correspondente no DB.
    Retorna o objeto TokenData.
    """
    token_data = decode_access_token(token) # Usa a função de decodificação

    # Esta parte é para validação de EXISTÊNCIA e ATIVIDADE do usuário no DB.
    # Não altere o que é retornado no final da função!
    if token_data.user_type == "admin":
        user_in_db = db.query(AdminUser).filter(AdminUser.id == token_data.id).first()
        if not user_in_db or (hasattr(user_in_db, 'is_active') and not user_in_db.is_active):
            logger.warning(f"AdminUser com ID '{token_data.id}' não encontrado ou inativo para token válido.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrador não encontrado ou inativo.")
        logger.info(f"AdminUser ID {user_in_db.id} autenticado via token.")
    elif token_data.user_type == "user":
        user_in_db = db.query(User).filter(User.id == token_data.id).first()
        if not user_in_db or (hasattr(user_in_db, 'is_active') and not user_in_db.is_active):
            logger.warning(f"User com ID '{token_data.id}' não encontrado ou inativo para token válido.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado ou inativo.")
        logger.info(f"User ID {user_in_db.id} autenticado via token.")
    else:
        logger.error(f"Tipo de usuário desconhecido no token: '{token_data.user_type}'")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tipo de usuário não reconhecido.")

    # AQUI ESTÁ A MUDANÇA MAIS IMPORTANTE:
    # Retorne o objeto TokenData que você decodificou, não o objeto do DB.
    return token_data


# --- Funções de Dependência Específicas por Tipo de Usuário (OPCIONAIS, se precisar do OBJETO ORM) ---

async def get_current_admin_user(
    token_data: TokenData = Depends(get_current_user_from_token), # Dependa de TokenData agora
    db: Session = Depends(get_db)
) -> AdminUser:
    """
    Dependência que garante que o usuário autenticado é um AdminUser E retorna o objeto ORM AdminUser.
    """
    if token_data.user_type != "admin": # Use o user_type de TokenData
        logger.warning(f"Acesso negado: Usuário ID '{token_data.id}' (tipo '{token_data.user_type}') tentou acessar rota de admin.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação não permitida. Requer privilégios de administrador."
        )
    # Agora busque o AdminUser real do banco de dados
    admin_user_in_db = db.query(AdminUser).filter(AdminUser.id == token_data.id).first()
    if not admin_user_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrador não encontrado no DB.")
    return admin_user_in_db


async def get_current_common_user(
    token_data: TokenData = Depends(get_current_user_from_token), # Dependa de TokenData agora
    db: Session = Depends(get_db)
) -> User:
    """
    Dependência que garante que o usuário autenticado é um User comum E retorna o objeto ORM User.
    """
    if token_data.user_type != "user": # Use o user_type de TokenData
        logger.warning(f"Acesso negado: Usuário ID '{token_data.id}' (tipo '{token_data.user_type}') tentou acessar rota de usuário comum.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação não permitida. Requer privilégios de usuário comum."
        )
    # Agora busque o User real do banco de dados
    user_in_db = db.query(User).filter(User.id == token_data.id).first()
    if not user_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado no DB.")
    return user_in_db