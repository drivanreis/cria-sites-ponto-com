# File: backend/src/routers/employee_routers.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.cruds import employee_cruds
from src.schemas.employee_schemas import EmployeeRead, EmployeeUpdate, EmployeeCreateInternal
from src.db.database import get_db
from src.models.employee_models import Base, Employee
from src.dependencies.oauth2 import get_current_admin_user # Importa a dependência de segurança para admin

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)

# --- Lógica de Inicialização (Startup Event) ---
# Esta função será executada quando a aplicação iniciar.
# Conforme a nossa discussão, esta lógica será MOVIDA para main.py
# e, portanto, será REMOVIDA deste arquivo no PRÓXIMO PASSO (main.py).
# Por agora, estou mantendo-a para o fluxo da revisão, mas ela será removida.
@router.on_event("startup")
async def startup_event():
    db: Session = next(get_db())
    try:
        Base.metadata.create_all(bind=db.get_bind())

        required_employees_data = [
            {
                "employee_name": "Entrevistador Pessoal",
                "employee_script": {"intro": "Olá, sou seu entrevistador pessoal."},
                "ia_name": "Gemini",
                "endpoint_url": "https://api.gemini.com/v1/interview",
                "endpoint_key": "GEMINI_KEY_123",
                "headers_template": {"Content-Type": "application/json"},
                "body_template": {"model": "gemini-pro", "prompt": "{user_input}"}
            },
            {
                "employee_name": "Suporte Técnico",
                "employee_script": {"greeting": "Bem-vindo ao suporte técnico."},
                "ia_name": "ChatGPT",
                "endpoint_url": "https://api.openai.com/v1/chat",
                "endpoint_key": "OPENAI_KEY_456",
                "headers_template": {"Authorization": "Bearer {api_key}"},
                "body_template": {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "{user_query}"}]}
            },
            {
                "employee_name": "Consultor Financeiro",
                "employee_script": {"advice": "Estou aqui para ajudar com suas finanças."},
                "ia_name": "DeepSeek",
                "endpoint_url": "https://api.deepseek.com/v1/advice",
                "endpoint_key": "DEEPSEEK_KEY_789",
                "headers_template": {"X-Api-Key": "{api_key}"},
                "body_template": {"role": "consultant", "query": "{user_request}"}
            }
        ]

        for emp_data_raw in required_employees_data:
            validated_data = EmployeeCreateInternal(**emp_data_raw)
            existing_employee = employee_cruds.get_employee_by_name(db, employee_name=validated_data.employee_name)
            
            if not existing_employee:
                print(f"Criando registro de funcionário mínimo: {validated_data.employee_name}")
                employee_cruds.create_employee_initial(db, validated_data)
            else:
                print(f"Registro de funcionário mínimo já existe: {validated_data.employee_name}")
    finally:
        db.close()

# --- Rotas da API ---
# Todas as rotas abaixo AGORA exigirão um token válido DE UM ADMINISTRADOR.
# O parâmetro 'current_admin_user' receberá os dados do token (id, username, user_type)
# Se o token for inválido, ausente ou o user_type não for 'admin',
# a dependência get_current_admin_user levantará uma HTTPException 401 UNAUTHORIZED ou 403 FORBIDDEN.

@router.get("/", response_model=List[EmployeeRead])
def read_employees(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin_user: dict = Depends(get_current_admin_user) # Protegido para admin
):
    """
    Retorna uma lista de todos os funcionários. Apenas administradores podem acessar.
    """
    employees = employee_cruds.get_all_employees(db, skip=skip, limit=limit)
    return employees

@router.get("/{employee_id}", response_model=EmployeeRead)
def read_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_admin_user: dict = Depends(get_current_admin_user) # Protegido para admin
):
    """
    Retorna um funcionário específico pelo seu ID. Apenas administradores podem acessar.
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
    current_admin_user: dict = Depends(get_current_admin_user) # Protegido para admin
):
    """
    Atualiza um funcionário existente. O campo 'employee_name' não pode ser modificado. Apenas administradores podem acessar.
    """
    # CORREÇÃO: Chamar a função update_employee do módulo employee_cruds, não do objeto 'employee'
    db_employee = employee_cruds.update_employee(db, employee_id=employee_id, employee_update_data=employee)
    if db_employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")
    return db_employee

# ROTAS POST (CRIAR) E DELETE (EXCLUIR) FORAM REMOVIDAS, CONFORME REQUERIDO.