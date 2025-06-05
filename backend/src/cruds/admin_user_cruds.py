# File: backend/src/cruds/admin_user_cruds.py

from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import logging

from src.models.admin_user_models import AdminUser
from src.schemas.admin_user_schemas import AdminUserCreate, AdminUserUpdate
from src.utils.datetime_utils import get_current_datetime_str
from src.core.security import get_password_hash, verify_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Funções CRUD ---

def get_admin_user(db: Session, admin_user_id: int) -> Optional[AdminUser]:
    """
    Busca um usuário administrador pelo seu ID.
    """
    logger.info(f"Buscando usuário administrador com ID: {admin_user_id}")
    return db.query(AdminUser).filter(AdminUser.id == admin_user_id).first()

def get_admin_user_by_username(db: Session, username: str) -> Optional[AdminUser]:
    """
    Busca um usuário administrador pelo seu nome de usuário.
    """
    logger.info(f"Buscando usuário administrador com username: '{username}'")
    return db.query(AdminUser).filter(AdminUser.username == username).first()

def get_admin_users(db: Session, skip: int = 0, limit: int = 100) -> List[AdminUser]:
    """
    Retorna uma lista de usuários administradores com paginação.
    """
    logger.info(f"Buscando lista de usuários administradores (skip={skip}, limit={limit})")
    return db.query(AdminUser).offset(skip).limit(limit).all()

def create_admin_user(db: Session, admin_user: AdminUserCreate) -> AdminUser:
    """
    Cria um novo usuário administrador no banco de dados.
    Espera que as validações de unicidade (username) sejam feitas ANTES
    de chamar esta função, idealmente na camada do router/serviço.
    """
    logger.info(f"Tentando criar novo usuário administrador com username: '{admin_user.username}'")
    
    hashed_password = get_password_hash(admin_user.password)
    
    db_admin_user = AdminUser(
        username=admin_user.username,
        password_hash=hashed_password,
        # two_factor_secret e is_two_factor_enabled terão valores padrão ou serão definidos via outra rota
        creation_date=get_current_datetime_str() # Preenche a data de criação
    )
    
    try:
        db.add(db_admin_user)
        db.commit()
        db.refresh(db_admin_user)
        logger.info(f"Usuário administrador criado com sucesso. ID: {db_admin_user.id}, Username: {db_admin_user.username}")
        return db_admin_user
    except IntegrityError as e:
        db.rollback()
        error_message = str(e.orig) # Pega a mensagem de erro original do DBAPI
        logger.error(f"Erro de integridade ao criar admin user: {error_message}")
        # Mantendo HTTPException aqui por consistência, mas idealmente CRUD levantaria exceção de domínio.
        if "UNIQUE constraint failed: admin_users.username" in error_message or "duplicate key value violates unique constraint \"ix_admin_users_username\"" in error_message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nome de usuário já registrado por outro administrador.")
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Dados duplicados. Verifique os campos únicos.")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro inesperado ao criar admin user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor ao criar admin user: {e}")


def update_admin_user(db: Session, admin_user_id: int, admin_user: AdminUserUpdate) -> Optional[AdminUser]:
    """
    Atualiza um registro de usuário administrador existente.
    """
    logger.info(f"Tentando atualizar admin user ID: {admin_user_id}")
    db_admin_user = db.query(AdminUser).filter(AdminUser.id == admin_user_id).first()
    
    if db_admin_user is None:
        logger.warning(f"Admin User ID {admin_user_id} não encontrado para atualização.")
        return None

    # Preparar os dados de atualização. admin_user.model_dump(exclude_unset=True) é para Pydantic V2
    # e garante que apenas campos fornecidos sejam considerados.
    update_data = admin_user.model_dump(exclude_unset=True)

    # Processar a senha separadamente, se fornecida
    if "password" in update_data and update_data["password"] is not None:
        update_data["password_hash"] = get_password_hash(update_data.pop("password")) # Substitui 'password' por 'password_hash'
    
    # Preencher os campos do modelo com os dados atualizados
    for key, value in update_data.items():
        setattr(db_admin_user, key, value)
    
    try:
        db.add(db_admin_user) # Adicionar novamente para garantir que o SQLAlchemy rastreie as mudanças
        db.commit()
        db.refresh(db_admin_user)
        logger.info(f"Admin User ID {admin_user_id} atualizado com sucesso.")
        return db_admin_user
    except IntegrityError as e:
        db.rollback()
        error_message = str(e.orig)
        logger.error(f"Erro de integridade ao atualizar admin user ID {admin_user_id}: {error_message}")
        if "UNIQUE constraint failed: admin_users.username" in error_message or "duplicate key value violates unique constraint \"ix_admin_users_username\"" in error_message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nome de usuário já registrado por outro administrador.")
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Dados duplicados. Verifique os campos únicos.")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro inesperado ao atualizar admin user ID {admin_user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor ao atualizar admin user: {e}")

def delete_admin_user(db: Session, admin_user_id: int) -> bool:
    """
    Deleta um registro de usuário administrador.
    """
    logger.info(f"Tentando deletar admin user ID: {admin_user_id}")
    db_admin_user = db.query(AdminUser).filter(AdminUser.id == admin_user_id).first()
    if db_admin_user:
        try:
            db.delete(db_admin_user)
            db.commit()
            logger.info(f"Admin User ID {admin_user_id} deletado com sucesso.")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Erro inesperado ao deletar admin user ID {admin_user_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor ao deletar admin user: {e}")
    logger.warning(f"Admin User ID {admin_user_id} não encontrado para deleção.")
    return False