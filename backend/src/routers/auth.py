# file: src/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta # Necessário para o timedelta de expiração do token
from sqlalchemy.orm import Session
from typing import Annotated, Union # Adicionado Union para tipagem

from src.db.database import get_db
from src.schemas.token import Token # <<< IMPORTANTE: Mantive esta importação para response_model=Token
from src.core.config import settings
from src.utils.datetime_utils import get_current_datetime_str # Para o last_login

# >>> IMPORTAÇÕES CHAVE DO NOVO MÓDULO DE SEGURANÇA <<<
from src.core.security import create_access_token, authenticate_user
# Importar os modelos de banco de dados para a verificação de tipo (isinstance)
from src.models.admin_user import AdminUser
from src.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# A função 'create_access_token' foi movida para src/core/security.py.
# A função 'authenticate_user' também foi definida lá e é a que vamos usar.

# Rota de Login UNIFICADA para AdminUser e User Comum
@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], # Usamos 'Annotated' para melhor tipagem
    db: Session = Depends(get_db)
):
    # Usa a função 'authenticate_user' do módulo security para tentar logar
    # form_data.username pode ser o username do admin, ou o email/telefone do usuário comum
    authenticated_entity: Union[AdminUser, User, None] = authenticate_user(db, form_data.username, form_data.password)

    if not authenticated_entity:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas ou usuário não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Define os dados para o token e o tempo de expiração com base no tipo de entidade autenticada
    user_id = authenticated_entity.id
    if isinstance(authenticated_entity, AdminUser):
        user_identifier_for_token = authenticated_entity.username # Para admins, o 'username' no token será o username
        user_type = "admin"
        access_token_expires = timedelta(minutes=settings.ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Atualiza o last_login do administrador
        authenticated_entity.last_login = get_current_datetime_str()
        db.add(authenticated_entity)
        db.commit()
        db.refresh(authenticated_entity)
    elif isinstance(authenticated_entity, User):
        user_identifier_for_token = authenticated_entity.email or authenticated_entity.phone_number # Para usuários comuns, será email ou telefone
        user_type = "user"
        access_token_expires = timedelta(minutes=settings.USER_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Opcional: Descomente as linhas abaixo se quiser atualizar o last_login para usuários comuns
        # authenticated_entity.last_login = get_current_datetime_str()
        # db.add(authenticated_entity)
        # db.commit()
        # db.refresh(authenticated_entity)
    else:
        # Isso não deve acontecer se a função authenticate_user estiver correta
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor ao determinar o tipo de usuário autenticado."
        )

    # Cria o token de acesso usando a função do módulo security
    access_token = create_access_token(
        data={
            "id": user_id,
            "username": user_identifier_for_token, # Este 'username' no token é o identificador de login (username, email ou telefone)
            "user_type": user_type
        },
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}