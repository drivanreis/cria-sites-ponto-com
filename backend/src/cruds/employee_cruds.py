# File: backend/src/crud/employee_cruds.py

from sqlalchemy.orm import Session
from sqlalchemy import exc
from typing import List, Optional
from src.utils.datetime_utils import get_current_datetime_str
from src.models.employee_models import Employee # Ajustada importação para employee_models.py
from src.schemas.employee_schemas import EmployeeUpdate, EmployeeCreateInternal # Ajustada importação para employee_schemas.py
from fastapi import HTTPException, status # Importar para levantar HTTPExceptions
import logging # Adicionado para logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_employee_by_id(db: Session, employee_id: int) -> Optional[Employee]:
    """
    Busca um funcionário pelo seu ID.
    """
    logger.info(f"Buscando funcionário com ID: {employee_id}")
    return db.query(Employee).filter(Employee.id == employee_id).first()

def get_employee_by_name(db: Session, sender_type: str) -> Optional[Employee]:
    """
    Busca um funcionário pelo seu nome (sender_type).
    """
    logger.info(f"Buscando funcionário com nome: '{sender_type}'")
    return db.query(Employee).filter(Employee.sender_type == sender_type).first()

def get_all_employees(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
    """
    Retorna uma lista de todos os funcionários, com paginação opcional.
    """
    logger.info(f"Buscando todos os funcionários (skip: {skip}, limit: {limit})")
    return db.query(Employee).offset(skip).limit(limit).all()

def create_employee_initial(db: Session, employee_data: EmployeeCreateInternal) -> Employee:
    """
    Cria um novo registro de funcionário no banco de dados.
    Esta função é destinada à inicialização da aplicação, não a uma rota POST.
    """
    logger.info(f"Tentando criar funcionário inicial: '{employee_data.sender_type}'")
    
    db_employee = Employee(
        sender_type=employee_data.sender_type,
        employee_script=employee_data.employee_script,
        ia_name=employee_data.ia_name,
        endpoint_url=employee_data.endpoint_url,
        endpoint_key=employee_data.endpoint_key,
        headers_template=employee_data.headers_template,
        body_template=employee_data.body_template,
        last_update=get_current_datetime_str()
    )
    try:
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        logger.info(f"Funcionário '{db_employee.sender_type}' criado com sucesso.")
        return db_employee
    except exc.IntegrityError:
        db.rollback()
        logger.warning(f"Tentativa de criar funcionário com nome duplicado: '{employee_data.sender_type}'")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Employee with this name already exists.")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro inesperado ao criar funcionário '{employee_data.sender_type}': {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor ao criar funcionário: {e}")

def update_employee(db: Session, employee_id: int, employee_update_data: EmployeeUpdate) -> Optional[Employee]:
    """
    Atualiza um registro de funcionário existente.
    O campo 'sender_type' não pode ser atualizado via esta função.
    """
    logger.info(f"Tentando atualizar funcionário ID: {employee_id}")
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        logger.warning(f"Tentativa de atualizar funcionário ID {employee_id} não encontrado.")
        return None

    update_data = employee_update_data.model_dump(exclude_unset=True)

    if "sender_type" in update_data:
        logger.warning(f"Tentativa de atualizar o nome do funcionário ID {employee_id}. Ignorando.")
        del update_data["sender_type"]

    for key, value in update_data.items():
        setattr(db_employee, key, value)

    db_employee.last_update = get_current_datetime_str()

    try:
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        logger.info(f"Funcionário ID {employee_id} atualizado com sucesso.")
        return db_employee
    except Exception as e:
        db.rollback()
        logger.error(f"Erro inesperado ao atualizar funcionário ID {employee_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno do servidor ao atualizar funcionário: {e}")

def delete_employee(db: Session, employee_id: int) -> bool:
    """
    Deleta um registro de funcionário.
    """
    logger.info(f"Tentando deletar funcionário ID: {employee_id}")
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if db_employee:
        db.delete(db_employee)
        db.commit()
        logger.info(f"Funcionário ID {employee_id} deletado com sucesso.")
        return True
    logger.warning(f"Tentativa de deletar funcionário ID {employee_id} não encontrado.")
    return False