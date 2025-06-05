# File: backend/src/routers/user_routers.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any # Adicionado Dict, Any para current_user_token

from src.cruds import user_cruds as crud_user
from src.schemas.user_schemas import UserCreate, UserUpdate, UserRead # CORREÇÃO: UserInDB renomeado para UserRead
from src.db.database import get_db
from src.dependencies.oauth2 import get_current_user_from_token
from src.schemas.token_schemas import TokenData

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# A rota de criação de usuário (POST /users/) geralmente é pública
# para permitir que novos usuários se registrem.
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED) # CORREÇÃO: response_model para UserRead
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Cria um novo usuário.
    Verifica se o email ou telefone já estão registrados antes de criar.
    """
    # Validação de duplicidade antes de tentar criar
    if user.email:
        db_user_by_email = crud_user.get_user_by_email(db, email=user.email)
        if db_user_by_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já registrado")
    
    # Verificação de phone_number duplicado
    if user.phone_number:
        db_user_by_phone = crud_user.get_user_by_phone_number(db, phone_number=user.phone_number)
        if db_user_by_phone:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Número de telefone já registrado")
    
    # Se nem email nem phone_number foram fornecidos, o validador do schema UserCreate já deveria ter pego.
    # Mas é bom ter um fallback ou confiar que o schema já lida com isso.
    # O schema UserCreate já tem um @model_validator para isso.
    # Se o email e phone_number forem None, o Pydantic já levanta ValueError.
    # Então, a linha abaixo é mais uma garantia ou para cenários onde a validação Pydantic é by-passada.
    if not user.email and not user.phone_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pelo menos um email ou um número de telefone deve ser fornecido para o cadastro.")

    try:
        db_user = crud_user.create_user(db=db, user=user)
        return db_user
    except HTTPException as e: # Captura HTTPExceptions levantadas pelo CRUD (ex: IntegrityError)
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor: {e}")


@router.get("/", response_model=List[UserRead]) # CORREÇÃO: response_model para List[UserRead]
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user_token: TokenData = Depends(get_current_user_from_token) # Apenas usuários autenticados
):
    """
    Retorna uma lista de usuários com paginação.
    Apenas administradores podem listar todos os usuários.
    """
    if current_user_token.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado. Apenas administradores podem listar usuários."
        )
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/me", response_model=UserRead) # CORREÇÃO: response_model para UserRead
def read_users_me(
    db: Session = Depends(get_db),
    current_user_token: TokenData = Depends(get_current_user_from_token)
):
    """
    Retorna os dados do usuário autenticado atualmente.
    """
    # A dependência get_current_user_from_token já garante que o usuário existe
    # e que o token é válido. current_user_token.id é o ID do usuário logado.
    user_id = current_user_token.id
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        # Isso não deveria acontecer se o token é válido e o usuário existe no DB
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário autenticado não encontrado.")
    return db_user

@router.get("/{user_id}", response_model=UserRead) # CORREÇÃO: response_model para UserRead
def read_specific_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user_token: TokenData = Depends(get_current_user_from_token)
):
    """
    Retorna um usuário específico pelo ID.
    Um usuário comum pode ver apenas seu próprio perfil.
    Um administrador pode ver qualquer perfil.
    """
    # Lógica de autorização: Um usuário pode ver seu próprio perfil, ou um admin pode ver qualquer um.
    if current_user_token.user_type == "user" and current_user_token.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a acessar o perfil de outro usuário."
        )

    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return db_user

@router.put("/{user_id}", response_model=UserRead) # CORREÇÃO: response_model para UserRead
def update_existing_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user_token: TokenData = Depends(get_current_user_from_token)
):
    """
    Atualiza um usuário existente.
    Um usuário comum pode atualizar seu próprio perfil.
    Um administrador pode atualizar qualquer perfil.
    """
    # Lógica de autorização: Um usuário pode atualizar seu próprio perfil, ou um admin pode atualizar qualquer um.
    if current_user_token.user_type == "user" and current_user_token.id != user_id:
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
    current_user_token: TokenData = Depends(get_current_user_from_token)
):
    """
    Deleta um usuário existente.
    Apenas administradores podem deletar usuários.
    """
    # Lógica de autorização: Apenas administradores podem deletar usuários.
    if current_user_token.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado. Apenas administradores podem deletar usuários."
        )
    
    # É uma boa prática verificar se o usuário existe antes de tentar deletar
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    deleted = crud_user.delete_user(db, user_id=user_id)
    if not deleted:
        # Isso só aconteceria se o delete_user do CRUD falhasse por um motivo inesperado
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao deletar o usuário.")