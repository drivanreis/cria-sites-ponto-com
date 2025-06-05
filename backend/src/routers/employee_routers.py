# File: backend/src/routers/employee_routers.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any # Adicionado Dict, Any para current_admin_user

from src.cruds import employee_cruds
from src.schemas.employee_schemas import EmployeeRead, EmployeeUpdate # EmployeeCreateInternal não é mais necessário aqui
from src.db.database import get_db
# from src.models.employee_models import Base, Employee # Base e Employee não são mais necessários aqui para startup_event
from src.services import connect_ai_service # Necessário para test_ai_connections
from src.dependencies.oauth2 import get_current_admin_user # Proteger as rotas de Employee

# CORRIGIDO: Adicionado prefix e tags para organização da API
router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)

# --- Lógica de Inicialização (Startup Event) MOVIDA para main.py ---
# A função @router.on_event("startup") async def startup_event():
# e as importações relacionadas (Base, EmployeeCreateInternal, required_employees_data)
# foram removidas deste arquivo.

# --- Rotas da API (Mantidas, agora protegidas para Admin) ---

@router.get("/", response_model=List[EmployeeRead])
def read_employees(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin_user: Dict[str, Any] = Depends(get_current_admin_user) # APENAS ADMIN PODE VER EMPLOYEES
):
    """
    Retorna uma lista de todos os funcionários.
    Rota protegida: Apenas administradores podem acessar.
    """
    employees = employee_cruds.get_all_employees(db, skip=skip, limit=limit)
    return employees

@router.get("/{employee_id}", response_model=EmployeeRead)
def read_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_admin_user: Dict[str, Any] = Depends(get_current_admin_user) # APENAS ADMIN PODE VER EMPLOYEES
):
    """
    Retorna um funcionário específico pelo seu ID.
    Rota protegida: Apenas administradores podem acessar.
    """
    db_employee = employee_cruds.get_employee_by_id(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")
    return db_employee

@router.put("/{employee_id}", response_model=EmployeeRead)
def update_existing_employee(
    employee_id: int,
    employee: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_admin_user: Dict[str, Any] = Depends(get_current_admin_user) # APENAS ADMIN PODE ATUALIZAR EMPLOYEES
):
    """
    Atualiza um funcionário existente. O campo 'sender_type' não pode ser modificado.
    Rota protegida: Apenas administradores podem acessar.
    """
    # Use o método do crud, não um método no schema
    db_employee = employee_cruds.update_employee(db, employee_id=employee_id, employee_update_data=employee)
    if db_employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")
    return db_employee

# ROTAS POST (CRIAR) E DELETE (EXCLUIR) FORAM REMOVIDAS, CONFORME PLANO ANTERIOR.
# Se precisar de um POST para criar, ele deve ser adicionado aqui com proteção de admin.

@router.get("/test_ai_connections", response_model=Dict[str, str])
async def test_all_ai_connections(
    db: Session = Depends(get_db),
    current_admin_user: Dict[str, Any] = Depends(get_current_admin_user) # APENAS ADMIN PODE TESTAR CONEXÕES
):
    """
    Testa a conectividade com as APIs de IA para todos os Employees configurados.
    Rota protegida: Apenas administradores podem acessar.
    """
    employees = employee_cruds.get_all_employees(db, skip=0, limit=100)
    results = {}
    test_question = "Quantas pernas tem um ser humano?" # Pergunta genérica para teste

    for employee in employees:
        try:
            response_text = await connect_ai_service.call_external_ai_api(
                employee.endpoint_url,
                employee.endpoint_key,
                employee.headers_template,
                employee.body_template,
                test_question,
                employee.ia_name
            )
            # Verifica se a resposta não é vazia e não é um erro óbvio da IA
            if response_text and len(response_text.strip()) > 0 and "error" not in response_text.lower():
                results[employee.sender_type] = "OK"
            else:
                results[employee.sender_type] = f"Failed (Resposta da IA: '{response_text.strip()[:100]}...')"
        except HTTPException as e:
            results[employee.sender_type] = f"Failed (HTTP Error: {e.detail})"
        except Exception as e:
            results[employee.sender_type] = f"Failed (Erro inesperado: {str(e)})"
    
    return results