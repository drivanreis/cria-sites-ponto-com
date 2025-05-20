# File: backend/src/cruds/employee.py

from sqlalchemy.orm import Session
from typing import List

from src.models.employee import Employee
from src.schemas.employee import EmployeeCreate, EmployeeUpdate
from src.utils.datetime_utils import get_current_datetime_brasilia
import bcrypt

def get_employee(db: Session, employee_id: int):
    return db.query(Employee).filter(Employee.id == employee_id).first()

def get_employee_by_email(db: Session, email: str):
    return db.query(Employee).filter(Employee.email == email).first()

def get_employees(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
    return db.query(Employee).offset(skip).limit(limit).all()

def create_employee(db: Session, employee: EmployeeCreate) -> Employee:
    hashed_password = bcrypt.hashpw(employee.password.encode('utf-8'), bcrypt.gensalt())
    
    db_employee = Employee(
        full_name=employee.full_name,
        email=employee.email,
        password=hashed_password.decode('utf-8'),
        phone_number=employee.phone_number,
        role=employee.role,
        is_active=employee.is_active,
        created_at=get_current_datetime_brasilia(),
        updated_at=get_current_datetime_brasilia()
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_employee(db: Session, employee_id: int, employee: EmployeeUpdate) -> Employee | None:
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if db_employee:
        for key, value in employee.dict(exclude_unset=True).items():
            if key == "password" and value:
                hashed_password = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt())
                setattr(db_employee, key, hashed_password.decode('utf-8'))
            else:
                setattr(db_employee, key, value)
        
        db_employee.updated_at = get_current_datetime_brasilia()
        db.commit()
        db.refresh(db_employee)
    return db_employee

def delete_employee(db: Session, employee_id: int) -> bool:
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if db_employee:
        db.delete(db_employee)
        db.commit()
        return True
    return False