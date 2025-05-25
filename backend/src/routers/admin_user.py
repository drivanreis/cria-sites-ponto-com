# File: backend/src/routers/admin_user.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from src.cruds import admin_user as crud_admin_user
from src.schemas.admin_user import AdminUserCreate, AdminUserUpdate, AdminUserInDB
from src.db.database import get_db
# >>> NOVIDADE: Importar a dependência de autenticação <<<
from src.dependencies.oauth2 import get_current_user_from_token
# >>> NOVIDADE: Importar TokenData para tipagem <<<
from src.schemas.token import TokenData # Usamos TokenData definido em schemas/token.py

router = APIRouter(
    prefix="/admin_users",
    tags=["Admin Users"]
)

# Todas as rotas abaixo AGORA exigirão um token válido
# O parâmetro 'current_user' receberá os dados do token (id, username, user_type)
# Se o token for inválido ou ausente, a dependência get_current_user_from_token
# levantará uma HTTPException 401 UNAUTHORIZED.

@router.post("/", response_model=AdminUserInDB, status_code=status.HTTP_201_CREATED)
def create_new_admin_user(
    admin_user: AdminUserCreate,
    db: Session = Depends(get_db),
    # >>> PROTEGER ESTA ROTA: Requer um token válido <<<
    current_user: TokenData = Depends(get_current_user_from_token)
):
    # Lógica de autorização (ex: apenas 'super_admin' pode criar outros admins)
    # Exemplo:
    # if current_user.user_type != "super_admin":
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    db_admin_user = crud_admin_user.get_admin_user_by_username(db, username=admin_user.username)
    if db_admin_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Admin user username already registered")
    return crud_admin_user.create_admin_user(db=db, admin_user=admin_user)

@router.get("/", response_model=List[AdminUserInDB])
def read_admin_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    # >>> PROTEGER ESTA ROTA: Requer um token válido <<<
    current_user: TokenData = Depends(get_current_user_from_token)
):
    # Lógica de autorização (ex: apenas admins podem listar outros admins)
    # Exemplo:
    # if current_user.user_type != "admin": # Ou uma role mais específica
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    admin_users = crud_admin_user.get_admin_users(db, skip=skip, limit=limit)
    return admin_users

@router.get("/{admin_user_id}", response_model=AdminUserInDB)
def read_admin_user(
    admin_user_id: int,
    db: Session = Depends(get_db),
    # >>> PROTEGER ESTA ROTA: Requer um token válido <<<
    current_user: TokenData = Depends(get_current_user_from_token)
):
    # Lógica de autorização (ex: um admin pode ver seu próprio perfil ou um super_admin pode ver qualquer um)
    # Exemplo:
    # if current_user.user_type == "admin" and current_user.id != admin_user_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this user")

    db_admin_user = crud_admin_user.get_admin_user(db, admin_user_id=admin_user_id)
    if db_admin_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found")
    return db_admin_user

@router.put("/{admin_user_id}", response_model=AdminUserInDB)
def update_existing_admin_user(
    admin_user_id: int,
    admin_user: AdminUserUpdate,
    db: Session = Depends(get_db),
    # >>> PROTEGER ESTA ROTA: Requer um token válido <<<
    current_user: TokenData = Depends(get_current_user_from_token)
):
    # Lógica de autorização (ex: um admin só pode atualizar o próprio perfil, a menos que seja um super_admin)
    # Exemplo:
    # if current_user.user_type == "admin" and current_user.id != admin_user_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")

    db_admin_user = crud_admin_user.update_admin_user(db, admin_user_id=admin_user_id, admin_user=admin_user)
    if db_admin_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found")
    return db_admin_user

@router.delete("/{admin_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_admin_user(
    admin_user_id: int,
    db: Session = Depends(get_db),
    # >>> PROTEGER ESTA ROTA: Requer um token válido <<<
    current_user: TokenData = Depends(get_current_user_from_token)
):
    # Lógica de autorização (ex: apenas um super_admin deve ser capaz de deletar outros admins)
    # Exemplo:
    # if current_user.user_type != "super_admin":
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    success = crud_admin_user.delete_admin_user(db, admin_user_id=admin_user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found")
    return