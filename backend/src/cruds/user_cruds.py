# File: backend/src/cruds/user_cruds.py

from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status # Manter por enquanto para exceções de Integridade, mas discutir abstração
import logging

from src.models.user_models import User
from src.schemas.user_schemas import UserCreate, UserUpdate
from src.utils.datetime_utils import get_current_datetime_str
from src.core.security import get_password_hash, verify_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Funções CRUD ---

def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    Busca um usuário pelo seu ID.
    """
    logger.info(f"Buscando usuário com ID: {user_id}")
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Busca um usuário pelo seu endereço de e-mail.
    """
    logger.info(f"Buscando usuário com email: '{email}'")
    return db.query(User).filter(User.email == email).first()

def get_user_by_phone_number(db: Session, phone_number: str) -> Optional[User]:
    """
    Busca um usuário pelo seu número de telefone.
    """
    logger.info(f"Buscando usuário com número de telefone: '{phone_number}'")
    return db.query(User).filter(User.phone_number == phone_number).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Retorna uma lista de usuários com paginação.
    """
    logger.info(f"Buscando lista de usuários (skip={skip}, limit={limit})")
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """
    Cria um novo usuário no banco de dados.
    Espera que as validações de unicidade (email/telefone) sejam feitas ANTES
    de chamar esta função, idealmente na camada do router/serviço.
    """
    logger.info(f"Tentando criar novo usuário com email: '{user.email}' ou telefone: '{user.phone_number}'")
    
    hashed_password = get_password_hash(user.password)
    
    db_user = User(
        name=user.name,
        email=user.email,
        phone_number=user.phone_number,
        password_hash=hashed_password,
        # Default values for these fields are set in the model, but can be explicitly set
        # email_verified=False,
        # is_two_factor_enabled=False,
        # status="active",
        creation_date=get_current_datetime_str() # Preenche a data de criação
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Usuário criado com sucesso. ID: {db_user.id}, Email: {db_user.email}")
        return db_user
    except IntegrityError as e:
        db.rollback()
        error_message = str(e.orig) # Pega a mensagem de erro original do DBAPI
        logger.error(f"Erro de integridade ao criar usuário: {error_message}")
        # NOVIDADE: O CRUD pode levantar uma exceção mais específica (não HTTP)
        # que o Router/Serviço irá capturar e traduzir para HTTPException.
        # Por enquanto, mantemos a HTTPException aqui para não quebrar o fluxo.
        if "UNIQUE constraint failed: users.email" in error_message or "duplicate key value violates unique constraint \"ix_users_email\"" in error_message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já registrado por outro usuário.")
        elif "UNIQUE constraint failed: users.phone_number" in error_message or "duplicate key value violates unique constraint \"ix_users_phone_number\"" in error_message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Número de telefone já registrado por outro usuário.")
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Dados duplicados. Verifique os campos únicos.")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro inesperado ao criar usuário: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor ao criar usuário: {e}")


def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    """
    Atualiza um registro de usuário existente.
    """
    logger.info(f"Tentando atualizar usuário ID: {user_id}")
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if db_user is None:
        logger.warning(f"Usuário ID {user_id} não encontrado para atualização.")
        return None # Ou levantar uma exceção específica para "Não Encontrado"

    # Preparar os dados de atualização. user.model_dump(exclude_unset=True) é para Pydantic V2
    # e garante que apenas campos fornecidos sejam considerados.
    update_data = user.model_dump(exclude_unset=True)

    # Processar a senha separadamente, se fornecida
    if "password" in update_data and update_data["password"] is not None:
        update_data["password_hash"] = get_password_hash(update_data.pop("password")) # Substitui 'password' por 'password_hash'
    
    # Preencher os campos do modelo com os dados atualizados
    for key, value in update_data.items():
        # Lógica para garantir que email/phone_number não sejam definidos como None se não forem passados
        # e já tiverem valor no DB, a menos que sejam explicitamente definidos como None no schema.
        # No nosso schema UserUpdate, eles são Optional[str] = None, então None é um valor válido se passado.
        setattr(db_user, key, value)
    
    try:
        db.add(db_user) # Adicionar novamente para garantir que o SQLAlchemy rastreie as mudanças
        db.commit()
        db.refresh(db_user)
        logger.info(f"Usuário ID {user_id} atualizado com sucesso.")
        return db_user
    except IntegrityError as e:
        db.rollback()
        error_message = str(e.orig)
        logger.error(f"Erro de integridade ao atualizar usuário ID {user_id}: {error_message}")
        if "UNIQUE constraint failed: users.email" in error_message or "duplicate key value violates unique constraint \"ix_users_email\"" in error_message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já registrado por outro usuário.")
        elif "UNIQUE constraint failed: users.phone_number" in error_message or "duplicate key value violates unique constraint \"ix_users_phone_number\"" in error_message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Número de telefone já registrado por outro usuário.")
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Dados duplicados. Verifique os campos únicos.")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro inesperado ao atualizar usuário ID {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor ao atualizar usuário: {e}")

def delete_user(db: Session, user_id: int) -> bool:
    """
    Deleta um registro de usuário.
    """
    logger.info(f"Tentando deletar usuário ID: {user_id}")
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        try:
            db.delete(db_user)
            db.commit()
            logger.info(f"Usuário ID {user_id} deletado com sucesso.")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Erro inesperado ao deletar usuário ID {user_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor ao deletar usuário: {e}")
    logger.warning(f"Usuário ID {user_id} não encontrado para deleção.")
    return False

# --- Funções de Autenticação (Podem ser movidas para um service ou Security Module) ---
# Embora você já tenha a função authenticate_user no security.py,
# estas funções auxiliares internas do CRUD podem ser úteis em certos cenários.
# No entanto, para o SRP, é melhor que a lógica de "verificar senha" esteja no security.py
# e o CRUD se foque apenas em obter o usuário.

def get_user_by_identifier(db: Session, identifier: str) -> Optional[User]:
    """
    Busca um usuário por email ou telefone.
    """
    user = get_user_by_email(db, identifier)
    if user:
        return user
    user = get_user_by_phone_number(db, identifier)
    if user:
        return user
    return None

def verify_user_password(db: Session, user_id: int, plain_password: str) -> bool:
    """
    Verifica a senha de um usuário pelo ID.
    """
    db_user = get_user(db, user_id)
    if db_user and db_user.password_hash:
        return verify_password(plain_password, db_user.password_hash)
    return False