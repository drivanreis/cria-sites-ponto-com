# File: backend/src/dependencies/oauth2.py

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

# Esquema OAuth2 para extrair o token do cabeçalho Authorization
# O tokenUrl deve apontar para a rota de login da sua aplicação
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") # Aponta para a rota de login unificada

# --- Funções de Decodificação e Validação de Token ---

def decode_access_token(token: str) -> TokenData:
    """
    Decodifica um token JWT e valida seu payload.
    Levanta HTTPException se o token for inválido ou expirado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Tenta decodificar o token usando a chave secreta e o algoritmo
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Extrai os dados do payload e valida-os com o schema TokenData
        token_id: int = payload.get("id")
        token_username: str = payload.get("username")
        token_user_type: str = payload.get("user_type")
        token_email: Optional[str] = payload.get("email") # Captura o email se presente no token

        if token_id is None or token_username is None or token_user_type is None:
            raise credentials_exception
        
        # Retorna uma instância de TokenData
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
) -> Union[AdminUser, User]: # Pode retornar um AdminUser ou um User
    """
    Dependência que valida o token, decodifica-o e busca o usuário correspondente no DB.
    Retorna o objeto AdminUser ou User do banco de dados.
    """
    token_data = decode_access_token(token) # Usa a função de decodificação

    # Agora, buscar o usuário no banco de dados com base nas informações do token_data
    if token_data.user_type == "admin":
        user_in_db = db.query(AdminUser).filter(AdminUser.id == token_data.id).first()
        if not user_in_db:
            logger.warning(f"AdminUser com ID '{token_data.id}' não encontrado para token válido.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrador não encontrado.")
        logger.info(f"AdminUser ID {user_in_db.id} autenticado via token.")
        return user_in_db
    elif token_data.user_type == "user":
        # Pode buscar por ID, email ou phone_number dependendo de como o token foi criado
        user_in_db = db.query(User).filter(User.id == token_data.id).first()
        if not user_in_db:
            logger.warning(f"User com ID '{token_data.id}' não encontrado para token válido.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
        logger.info(f"User ID {user_in_db.id} autenticado via token.")
        return user_in_db
    else:
        logger.error(f"Tipo de usuário desconhecido no token: '{token_data.user_type}'")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tipo de usuário não reconhecido.")


# --- Funções de Dependência Específicas por Tipo de Usuário ---

async def get_current_admin_user(
    current_user: Union[AdminUser, User] = Depends(get_current_user_from_token)
) -> AdminUser:
    """
    Dependência que garante que o usuário autenticado é um AdminUser.
    Retorna o objeto AdminUser.
    """
    if not isinstance(current_user, AdminUser):
        logger.warning(f"Acesso negado: Usuário ID '{current_user.id}' (tipo '{current_user.user_type if hasattr(current_user, 'user_type') else 'desconhecido'}') tentou acessar rota de admin.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação não permitida. Requer privilégios de administrador."
        )
    return current_user # Já é um AdminUser

async def get_current_common_user(
    current_user: Union[AdminUser, User] = Depends(get_current_user_from_token)
) -> User:
    """
    Dependência que garante que o usuário autenticado é um User comum.
    Retorna o objeto User.
    """
    if not isinstance(current_user, User):
        logger.warning(f"Acesso negado: Usuário ID '{current_user.id}' (tipo '{current_user.user_type if hasattr(current_user, 'user_type') else 'desconhecido'}') tentou acessar rota de usuário comum.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação não permitida. Requer privilégios de usuário comum."
        )
    return current_user # Já é um User