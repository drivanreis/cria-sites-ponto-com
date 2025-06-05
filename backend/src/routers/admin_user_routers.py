# File: backend/src/routers/admin_user_routers.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from src.cruds import admin_user_cruds
from src.schemas.admin_user_schemas import AdminUserCreate, AdminUserUpdate, AdminUserRead # CORREÇÃO: AdminUserInDB renomeado para AdminUserRead
from src.db.database import get_db
# CORREÇÃO: Usar get_current_user_from_token diretamente ou ter um get_current_admin_user que retorne TokenData
from src.dependencies.oauth2 import get_current_user_from_token
from src.schemas.token_schemas import TokenData # Importar TokenData para tipagem

router = APIRouter(
    prefix="/admin_users",
    tags=["Admin Users"]
)

# Todas as rotas abaixo AGORA exigirão um token válido DE UM ADMINISTRADOR.
# A dependência get_current_user_from_token já valida o token e o tipo de usuário.
# Se o token for inválido, ausente ou o user_type não for 'admin',
# a dependência levantará uma HTTPException 401 UNAUTHORIZED ou 403 FORBIDDEN.

@router.post("/", response_model=AdminUserRead, status_code=status.HTTP_201_CREATED) # CORREÇÃO: response_model para AdminUserRead
def create_new_admin_user(
    admin_user: AdminUserCreate,
    db: Session = Depends(get_db),
    # QUALQUER ADMIN PODE CRIAR NOVOS ADMINS.
    current_admin_token: TokenData = Depends(get_current_user_from_token) # Usamos TokenData para tipagem
):
    """
    Cria um novo usuário administrador.
    Requer privilégios de 'admin' para criar outros administradores.
    Verifica se o nome de usuário já está em uso.
    """
    # Verifica se o usuário autenticado é um administrador (não 'super_admin', apenas 'admin')
    if current_admin_token.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação não permitida. Requer privilégios de administrador."
        )

    # Validação de duplicidade antes de tentar criar (melhora a experiência do usuário)
    db_admin_by_username = admin_user_cruds.get_admin_user_by_username(db, username=admin_user.username)
    if db_admin_by_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nome de usuário já registrado por outro administrador.")

    try:
        db_admin = admin_user_cruds.create_admin_user(db=db, admin_user=admin_user)
        return db_admin
    except HTTPException as e: # Captura HTTPExceptions levantadas pelo CRUD (ex: IntegrityError)
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor: {e}")


@router.get("/", response_model=List[AdminUserRead]) # CORREÇÃO: response_model para List[AdminUserRead]
def read_admin_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin_token: TokenData = Depends(get_current_user_from_token) # Apenas usuários autenticados como admin
):
    """
    Retorna uma lista de usuários administradores com paginação.
    Requer privilégios de 'admin'.
    """
    # A dependência get_current_user_from_token já deve ter validado que o user_type é 'admin'.
    # Se ela não retornar "admin" (e sim "user"), a requisição já teria sido barrada.
    # Mas para clareza e segurança explícita:
    if current_admin_token.user_type != "admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operação não permitida. Requer privilégios de administrador.")
    
    admin_users = admin_user_cruds.get_admin_users(db, skip=skip, limit=limit)
    return admin_users

@router.get("/me", response_model=AdminUserRead) # Rota para o próprio admin
def read_admin_users_me(
    db: Session = Depends(get_db),
    current_admin_token: TokenData = Depends(get_current_user_from_token)
):
    """
    Retorna os dados do usuário administrador autenticado atualmente.
    Requer privilégios de 'admin'.
    """
    # current_admin_token.id é o ID do admin logado.
    # A dependência get_current_user_from_token já garante que user_type é 'admin'.
    if current_admin_token.user_type != "admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operação não permitida. Requer privilégios de administrador.")

    admin_user_id = current_admin_token.id
    db_admin_user = admin_user_cruds.get_admin_user(db, admin_user_id=admin_user_id)
    if db_admin_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrador autenticado não encontrado.")
    return db_admin_user


@router.get("/{admin_user_id}", response_model=AdminUserRead) # CORREÇÃO: response_model para AdminUserRead
def read_specific_admin_user(
    admin_user_id: int,
    db: Session = Depends(get_db),
    current_admin_token: TokenData = Depends(get_current_user_from_token)
):
    """
    Retorna um usuário administrador específico pelo ID.
    Qualquer administrador pode ver o perfil de outro administrador.
    """
    # Lógica de autorização: Qualquer admin pode ver o perfil de qualquer outro admin.
    if current_admin_token.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a acessar perfis de administradores."
        )
    
    db_admin_user = admin_user_cruds.get_admin_user(db, admin_user_id=admin_user_id)
    if db_admin_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin Usuário não encontrado")
    return db_admin_user


@router.put("/{admin_user_id}", response_model=AdminUserRead) # CORREÇÃO: response_model para AdminUserRead
def update_existing_admin_user(
    admin_user_id: int,
    admin_user: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_admin_token: TokenData = Depends(get_current_user_from_token)
):
    """
    Atualiza um usuário administrador existente.
    Qualquer administrador pode atualizar o perfil de outro administrador.
    """
    # Lógica de autorização: Qualquer admin pode atualizar o perfil de qualquer outro admin.
    if current_admin_token.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a atualizar perfis de administradores."
        )
    
    db_admin_user = admin_user_cruds.update_admin_user(db, admin_user_id=admin_user_id, admin_user=admin_user)
    if db_admin_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin Usuário não encontrado")
    return db_admin_user


@router.delete("/{admin_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_admin_user(
    admin_user_id: int,
    db: Session = Depends(get_db),
    current_admin_token: TokenData = Depends(get_current_user_from_token)
):
    """
    Deleta um usuário administrador existente.
    Qualquer administrador pode deletar outros administradores, inclusive a si mesmo.
    """
    # Lógica de autorização: Qualquer administrador pode deletar outros administradores.
    if current_admin_token.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação não permitida. Requer privilégios de administrador."
        )
    
    # NÃO HÁ RESTRIÇÃO PARA DELETAR A SI MESMO, conforme seu requisito.
    # CUIDADO: Se o último admin se deletar, não haverá mais acesso administrativo via login.

    db_admin_user = admin_user_cruds.get_admin_user(db, admin_user_id=admin_user_id)
    if db_admin_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin Usuário não encontrado")
    
    deleted = admin_user_cruds.delete_admin_user(db, admin_user_id=admin_user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao deletar o usuário administrador.")