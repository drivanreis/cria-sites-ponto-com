from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional

# >>> CORREÇÃO: Importar as configurações centralizadas <<<
from src.core.config import settings # Importa a instância 'settings' do nosso arquivo de configuração

# Define o endpoint onde o cliente pode obter um token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") # Manter tokenUrl como rota de login

# Esquema para o payload do token JWT
class TokenData(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None # Para login de admin_user (e também de user, se usarmos username)
    email: Optional[str] = None # Para login de user (se usarmos email)
    user_type: Optional[str] = None # 'admin' ou 'user'

async def get_current_user_from_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # >>> CORREÇÃO: Usar as configurações de 'settings' <<<
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        user_id: int = payload.get("id")
        username: Optional[str] = payload.get("username") # Pode ser nulo se o user_type for 'user' e usar email
        email: Optional[str] = payload.get("email") # Pode ser nulo se o user_type for 'admin'
        user_type: str = payload.get("user_type")

        # Verifica se pelo menos um identificador (id ou username/email) e o tipo de usuário existem
        if user_id is None or user_type is None or (username is None and email is None):
            raise credentials_exception
        
        token_data = TokenData(id=user_id, username=username, email=email, user_type=user_type)
        
    except JWTError:
        raise credentials_exception
    
    return token_data

# Este arquivo está pronto para ser usado como dependência!