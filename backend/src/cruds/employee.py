# File: backend/src/cruds/employee.py

from sqlalchemy.orm import Session
from typing import List, Optional # Importar Optional para tipos de retorno
from datetime import datetime # Para usar datetime.now() ou similar

from src.models.employee import Employee
from src.schemas.employee import EmployeeCreate, EmployeeUpdate
# from src.utils.datetime_utils import get_current_datetime_brasilia # Remover se não for mais usado

# Funções auxiliares para buscar employees
def get_employee(db: Session, employee_id: int) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.id == employee_id).first()

# REMOVIDO: get_employee_by_email - O modelo Employee não tem campo 'email'
# def get_employee_by_email(db: Session, email: str):
#     return db.query(Employee).filter(Employee.email == email).first()

# Adicione esta função em backend/src/cruds/employee.py
# (Pode ser logo abaixo de get_employee, por exemplo)

def get_employee_by_role_name(db: Session, role_name: str) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.role_name == role_name).first()


def get_employees(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
    return db.query(Employee).offset(skip).limit(limit).all()

# Função para criar um novo employee (persona de IA)
def create_employee(db: Session, employee: EmployeeCreate) -> Employee:
    # REMOVIDO: Lógica de hashing de senha - Employees não têm senha
    
    db_employee = Employee(
        role_name=employee.role_name,
        display_name=employee.display_name,
        ai_service_name=employee.ai_service_name,
        endpoint=employee.endpoint,
        model=employee.model,
        api_key_env_var_name=employee.api_key_env_var_name,
        initial_pre_prompt=employee.initial_pre_prompt,
        # context_instructions é opcional, então pode ser None se não for fornecido
        context_instructions=employee.context_instructions,
        # creation_date é server_default=CURRENT_TIMESTAMP no modelo, não precisa ser definido aqui
        # update_date é nullable, será definido na atualização
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

# Função para atualizar um employee existente
def update_employee(db: Session, employee_id: int, employee: EmployeeUpdate) -> Optional[Employee]:
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if db_employee:
        # Itera sobre os campos fornecidos no schema de atualização
        for key, value in employee.dict(exclude_unset=True).items():
            # REMOVIDO: Lógica de hashing de senha - Employees não têm senha
            # REMOVIDO: Mapeamento de campos que não existem no modelo Employee
            # Ex: 'full_name', 'email', 'phone_number', 'role', 'is_active'

            # Apenas atribui o valor se o campo existir no modelo Employee
            if hasattr(db_employee, key):
                setattr(db_employee, key, value)
        
        # Atualiza a data de modificação (se o modelo tiver 'update_date')
        # O modelo Employee tem 'update_date', então podemos atualizá-lo aqui
        db_employee.update_date = datetime.now() # Ou get_current_datetime_brasilia() se você mantiver a função
        
        db.commit()
        db.refresh(db_employee)
    return db_employee

# Função para deletar um employee
def delete_employee(db: Session, employee_id: int) -> bool:
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if db_employee:
        db.delete(db_employee)
        db.commit()
        return True
    return False

# REMOVIDO: verify_password - Employees não têm senha para verificar
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))