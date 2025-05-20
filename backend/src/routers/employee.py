# File: backend/src/routers/employee.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.cruds import employee as crud_employee
from src.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeInDB
from src.db.database import get_db

router = APIRouter()

@router.post("/", response_model=EmployeeInDB, status_code=status.HTTP_201_CREATED)
def create_new_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = crud_employee.get_employee_by_email(db, email=employee.email)
    if db_employee:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Employee email already registered")
    return crud_employee.create_employee(db=db, employee=employee)

@router.get("/", response_model=List[EmployeeInDB])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    employees = crud_employee.get_employees(db, skip=skip, limit=limit)
    return employees

@router.get("/{employee_id}", response_model=EmployeeInDB)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = crud_employee.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return db_employee

@router.put("/{employee_id}", response_model=EmployeeInDB)
def update_existing_employee(employee_id: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    db_employee = crud_employee.update_employee(db, employee_id=employee_id, employee=employee)
    if db_employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return db_employee

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_employee(employee_id: int, db: Session = Depends(get_db)):
    success = crud_employee.delete_employee(db, employee_id=employee_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return {"message": "Employee deleted successfully"}