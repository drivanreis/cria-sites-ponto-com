from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional, Union # Adicionado Union

# Importar as configurações centralizadas
from src.core.config import settings

# Define o endpoint onde o cliente pode obter um token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Esquema para o payload do token JWT
class TokenData(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None # Para login de admin_user (ou username de user)
    # O campo 'email' não é mais diretamente lido do payload, pois 'username' já serve para ambos.
    # Pode ser removido ou mantido como None se não for usado. Vamos mantê-lo por segurança
    # para não causar conflitos em outros locais se for referenciado.
    email: Optional[str] = None 
    user_type: Optional[str] = None # 'admin' ou 'user'

async def get_current_user_from_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        user_id: int = payload.get("id")
        username: Optional[str] = payload.get("username") # Este será o identificador de login (username ou email/telefone)
        user_type: str = payload.get("user_type")

        # Verifica se o ID e o tipo de usuário existem no token
        if user_id is None or user_type is None:
            raise credentials_exception
        
        # Cria o objeto TokenData. O campo 'email' do TokenData será preenchido pelo 'username' do payload
        # se o user_type for 'user' e o identificador for um email.
        # Para admins, 'email' será None e 'username' será o username do admin.
        token_data = TokenData(
            id=user_id,
            username=username, # 'username' do TokenData recebe o identificador do token
            email=username if user_type == 'user' and '@' in username else None, # Tenta preencher email se for user e tiver @
            user_type=user_type
        )
        
    except JWTError:
        raise credentials_exception
    
    return token_data

# >>> NOVIDADE/CORREÇÃO CHAVE: Dependência para verificar se o usuário atual é um ADMINISTRADOR <<<
async def get_current_admin_user(current_user: TokenData = Depends(get_current_user_from_token)):
    """
    Dependência que verifica se o token pertence a um usuário com user_type 'admin'.
    Se não for admin, levanta uma exceção HTTP 403 FORBIDDEN.
    """
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação não permitida. Requer privilégios de administrador."
        )
    return current_user # Retorna o TokenData do admin (para uso posterior na rota, se necessário)

# Este arquivo está pronto para ser usado como dependência!