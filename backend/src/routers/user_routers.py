# File: backend/src/routers/user_routers.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.cruds import user_cruds as crud_user
from src.schemas.user_schemas import UserCreate, UserUpdate, UserRead
from src.db.database import get_db
from src.dependencies.oauth_file import get_current_admin_user, get_current_common_user
from src.models.user_models import User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# --- Criacao de usuario (aberto) ---
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = crud_user.create_user(db=db, user=user)
        return db_user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor: {e}")

# --- Lista de usuarios (apenas admin) ---
@router.get("/", response_model=List[UserRead])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

# --- Leitura do proprio perfil (/users/me) ---
@router.get("/me", response_model=UserRead)
def read_own_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_common_user)
):
    db_user = crud_user.get_user(db, user_id=current_user.id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário autenticado não encontrado.")
    return db_user

# --- Atualizacao do proprio perfil (/users/me) ---
@router.put("/me", response_model=UserRead)
def update_own_profile(
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_common_user)
):
    db_user = crud_user.update_user(db, user_id=current_user.id, user=user)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return db_user

# --- Leitura de usuario especifico (admin ou self) ---
@router.get("/{user_id}", response_model=UserRead)
def read_specific_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_common_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não autorizado a acessar outro perfil.")

    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return db_user

# --- Atualizacao de outro usuario (apenas admin) ---
@router.put("/{user_id}", response_model=UserRead)
def update_existing_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    db_user = crud_user.update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return db_user

# --- Exclusao de usuario (apenas admin) ---
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    deleted = crud_user.delete_user(db, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao deletar o usuário.")
