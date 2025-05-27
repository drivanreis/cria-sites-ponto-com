# File: backend/src/routers/employee.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional # Importar Optional

from src.cruds import employee as crud_employee
from src.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeInDB
from src.db.database import get_db

# CORRIGIDO: Adicionado prefix e tags para organização da API
router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)

@router.post("/", response_model=EmployeeInDB, status_code=status.HTTP_201_CREATED)
def create_new_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    # CORRIGIDO: Remover verificação por email, pois Employee não tem email.
    # Em vez disso, verificar se já existe um Employee com o mesmo role_name, que é unique.
    # Para isso, precisamos de uma função get_employee_by_role_name no CRUD de employee.
    # Por enquanto, vamos criar a função no CRUD e chamá-la aqui.

    # Vamos adicionar a função ao crud/employee.py primeiro para que possamos usá-la aqui.
    # Considerando que ela foi adicionada lá, o código abaixo estará correto.
    db_employee_exists = crud_employee.get_employee_by_role_name(db, role_name=employee.role_name)
    if db_employee_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Funcionário com nome de função '{employee.role_name}' já registrado"
        )
    
    return crud_employee.create_employee(db=db, employee=employee)

@router.get("/", response_model=List[EmployeeInDB])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    employees = crud_employee.get_employees(db, skip=skip, limit=limit)
    return employees

@router.get("/{employee_id}", response_model=EmployeeInDB)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = crud_employee.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")
    return db_employee

@router.put("/{employee_id}", response_model=EmployeeInDB)
def update_existing_employee(employee_id: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    db_employee = crud_employee.update_employee(db, employee_id=employee_id, employee=employee)
    if db_employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")
    return db_employee

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_employee(employee_id: int, db: Session = Depends(get_db)):
    success = crud_employee.delete_employee(db, employee_id=employee_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")
    # CORRIGIDO: Para 204 No Content, o corpo da resposta deve ser vazio.
    return

