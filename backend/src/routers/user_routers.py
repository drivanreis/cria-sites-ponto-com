# File: backend/src/routers/user.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from src.cruds import user_cruds as crud_user
from src.schemas.user_schemas import UserCreate, UserUpdate, UserInDB
from src.db.database import get_db
# >>> NOVIDADE: Importar a dependência de autenticação <<<
from src.dependencies.oauth2 import get_current_user_from_token
# >>> NOVIDADE: Importar TokenData para tipagem <<<
from src.schemas.token_schemas import TokenData

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# A rota de criação de usuário (POST /users/) geralmente é pública
# para permitir que novos usuários se registrem.
@router.post("/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    # Validação de duplicidade antes de tentar criar
    if user.email:
        db_user_by_email = crud_user.get_user_by_email(db, email=user.email)
        if db_user_by_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já registrado")
    
    # Verificação de phone_number duplicado
    if user.phone_number: # Verifica se phone_number foi fornecido
        db_user_by_phone = crud_user.get_user_by_phone_number(db, phone_number=user.phone_number)
        if db_user_by_phone:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Número de telefone já registrado")
            
    return crud_user.create_user(db=db, user=user)


# >>> NOVIDADE: Endpoint para obter o próprio usuário logado (/users/me) <<<
@router.get("/me", response_model=UserInDB)
def read_users_me(
    current_user: TokenData = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    # O ID do usuário já está no token, então podemos usá-lo diretamente
    db_user = crud_user.get_user(db, user_id=current_user.id)
    if db_user is None:
        # Isso não deveria acontecer se o token é válido e o usuário existe
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado (token inválido ou usuário deletado).")
    return db_user


@router.get("/", response_model=List[UserInDB])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_from_token)
):
    # Lógica de autorização: Apenas administradores podem listar todos os usuários.
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado. Apenas administradores podem listar usuários."
        )
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserInDB)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_from_token)
):
    # Lógica de autorização: Um usuário pode ver seu próprio perfil, ou um admin pode ver qualquer um.
    if current_user.user_type == "user" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a visualizar o perfil de outro usuário."
        )
    
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return db_user

@router.put("/{user_id}", response_model=UserInDB)
def update_existing_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_from_token)
):
    # Lógica de autorização: Um usuário pode atualizar seu próprio perfil, ou um admin pode atualizar qualquer um.
    if current_user.user_type == "user" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a atualizar o perfil de outro usuário."
        )

    db_user = crud_user.update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_from_token)
):
    # Lógica de autorização: Apenas administradores podem deletar usuários.
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado. Apenas administradores podem deletar usuários."
        )

    success = crud_user.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return