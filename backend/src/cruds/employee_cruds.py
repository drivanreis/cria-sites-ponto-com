# File: backend/src/crud/employee_cruds.py

from sqlalchemy.orm import Session
from sqlalchemy import exc
from src.utils.datetime_utils import get_current_datetime_str
from ..models.employee_models import Employee # Ajustada importação para employee_models.py
from ..schemas.employee_schemas import EmployeeUpdate, EmployeeCreateInternal # Ajustada importação para employee_schemas.py

def get_employee_by_id(db: Session, employee_id: int):
    """
    Busca um funcionário pelo seu ID.
    """
    return db.query(Employee).filter(Employee.id == employee_id).first()

def get_employee_by_name(db: Session, employee_name: str):
    """
    Busca um funcionário pelo seu nome (employee_name).
    """
    return db.query(Employee).filter(Employee.employee_name == employee_name).first()

def get_all_employees(db: Session, skip: int = 0, limit: int = 100):
    """
    Retorna uma lista de todos os funcionários, com paginação opcional.
    """
    return db.query(Employee).offset(skip).limit(limit).all()

def create_employee_initial(db: Session, employee_data: EmployeeCreateInternal):
    """
    Cria um novo registro de funcionário no banco de dados.
    Esta função é destinada à inicialização da aplicação, não a uma rota POST.
    """
    db_employee = Employee(
        employee_name=employee_data.employee_name,
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
        return db_employee
    except exc.IntegrityError:
        db.rollback()
        raise ValueError("Employee with this name already exists.")
    except Exception as e:
        db.rollback()
        raise e

def update_employee(db: Session, employee_id: int, employee_update_data: EmployeeUpdate):
    """
    Atualiza um registro de funcionário existente.
    O campo 'employee_name' não pode ser atualizado via esta função.
    """
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        return None

    update_data = employee_update_data.model_dump(exclude_unset=True)

    if "employee_name" in update_data:
        del update_data["employee_name"]

    for key, value in update_data.items():
        setattr(db_employee, key, value)

    db_employee.last_update = get_current_datetime_str()

    try:
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee
    except Exception as e:
        db.rollback()
        raise e