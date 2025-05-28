# File: backend/tests/employees/test_employees_permissions.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Importe as funções auxiliares do conftest.py
from tests.conftest import create_test_user, get_user_token, create_test_employee, get_admin_token
from src.models.employee_models import Employee # Para criar dados de teste no DB

# --- Testes de Permissão para GET /employees ---

def test_get_all_employees_as_regular_user_forbidden(client: TestClient, db_session_override: Session):
    """
    Testa se um usuário comum NÃO pode listar todos os funcionários (deve ser 403 Forbidden).
    """
    user_password = "UserEmployeeList123!"
    user_credentials = create_test_user(db_session_override, "Regular User List", "regular.employee.list@example.com", user_password)
    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get("/employees/", headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Operação não permitida. Requer privilégios de administrador."

def test_get_all_employees_no_token_unauthorized(client: TestClient):
    """
    Testa se a listagem de funcionários sem token retorna 401 Unauthorized.
    """
    response = client.get("/employees/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# --- Testes de Permissão para GET /employees/{id} ---

def test_get_employee_by_id_as_regular_user_forbidden(client: TestClient, db_session_override: Session):
    """
    Testa se um usuário comum NÃO pode buscar um funcionário pelo ID (deve ser 403 Forbidden).
    """
    user_password = "UserEmployeeID123!"
    user_credentials = create_test_user(db_session_override, "Regular User ID", "regular.employee.id@example.com", user_password)
    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)
    headers = {"Authorization": f"Bearer {user_token}"}

    # Crie um funcionário de teste (mesmo que o user não deva acessá-lo)
    test_employee = create_test_employee(db_session_override, "Teste de Permissão ID")

    response = client.get(f"/employees/{test_employee.id}", headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Operação não permitida. Requer privilégios de administrador."

def test_get_employee_by_id_no_token_unauthorized(client: TestClient):
    """
    Testa se a busca de funcionário por ID sem token retorna 401 Unauthorized.
    """
    response = client.get("/employees/1") # ID arbitrário, o importante é a falta de autenticação

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# --- Testes de Permissão para PUT /employees/{id} ---

def test_update_employee_as_regular_user_forbidden(client: TestClient, db_session_override: Session):
    """
    Testa se um usuário comum NÃO pode atualizar um funcionário (deve ser 403 Forbidden).
    """
    user_password = "UserEmployeeUpdate123!"
    user_credentials = create_test_user(db_session_override, "Regular User Update", "regular.employee.update@example.com", user_password)
    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)
    headers = {"Authorization": f"Bearer {user_token}"}

    # Crie um funcionário para tentar atualizar
    employee_to_update = create_test_employee(db_session_override, "Original Funcionario")

    updated_data = {"ia_name": "ProibidoIA"}

    response = client.put(
        f"/employees/{employee_to_update.id}",
        json=updated_data,
        headers=headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Operação não permitida. Requer privilégios de administrador."

    # Verifique que o funcionário NÃO foi alterado no banco de dados
    db_employee_after_attempt = db_session_override.query(Employee).filter(Employee.id == employee_to_update.id).first()
    assert db_employee_after_attempt.ia_name != updated_data["ia_name"] # Deve ser diferente
    assert db_employee_after_attempt.ia_name == "TestIA" # Voltou para o padrão do create_test_employee

def test_update_employee_no_token_unauthorized(client: TestClient):
    """
    Testa se a atualização de funcionário sem token retorna 401 Unauthorized.
    """
    updated_data = {"ia_name": "UnauthorizedIA"}
    response = client.put(
        "/employees/1", # ID arbitrário
        json=updated_data
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"