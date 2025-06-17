# File: backend/tests/employees/test_employees_crud.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Importe as funções auxiliares do conftest.py
from tests.conftest import create_test_admin_user, get_admin_token, create_test_employee
from src.models.employee_models import Employee

# --- Testes de Leitura (GET) ---

def test_get_all_employees_as_admin(client: TestClient, db_session_override: Session):
    """
    Testa se um administrador pode listar todos os funcionários.
    """
    admin_password = "AdminEmployee123!"
    admin_user = create_test_admin_user(db_session_override, "admin_employee_list", admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_user.username, admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Crie alguns funcionários de teste
    employee1 = create_test_employee(db_session_override, "Entrevistador Pessoal")
    employee2 = create_test_employee(db_session_override, "Suporte Técnico")

    response = client.get("/employees/", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2 # Pode haver outros funcionários da inicialização
    
    # Verifica se os funcionários criados estão na lista
    employee_names = [emp["employee_name"] for emp in data]
    assert employee1.employee_name in employee_names
    assert employee2.employee_name in employee_names

def test_get_employee_by_id_as_admin(client: TestClient, db_session_override: Session):
    """
    Testa se um administrador pode buscar um funcionário pelo ID.
    """
    admin_password = "AdminEmployee456!"
    admin_user = create_test_admin_user(db_session_override, "admin_employee_id", admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_user.username, admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Crie um funcionário de teste
    test_employee = create_test_employee(db_session_override, "Consultor Financeiro")

    response = client.get(f"/employees/{test_employee.id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_employee.id
    assert data["employee_name"] == test_employee.employee_name
    assert "employee_script" in data
    assert "ia_name" in data

def test_get_employee_not_found_as_admin(client: TestClient, db_session_override: Session):
    """
    Testa se a busca por ID de funcionário não encontrado retorna 404.
    """
    admin_password = "AdminEmployee789!"
    admin_user = create_test_admin_user(db_session_override, "admin_employee_not_found", admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_user.username, admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    non_existent_id = 99999 # Um ID que certamente não existe

    response = client.get(f"/employees/{non_existent_id}", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Funcionário não encontrado"

# --- Testes de Atualização (PUT) ---

def test_update_employee_as_admin(client: TestClient, db_session_override: Session):
    """
    Testa se um administrador pode atualizar os dados de um funcionário.
    """
    admin_password = "AdminEmployeeUpdate1!"
    admin_user = create_test_admin_user(db_session_override, "admin_employee_update", admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_user.username, admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Crie um funcionário para ser atualizado
    employee_to_update = create_test_employee(db_session_override, "Atendente Virtual", ia_name="OldIA", endpoint_key="old_key")

    updated_data = {
        "ia_name": "NewIA",
        "endpoint_key": "new_key_123",
        "employee_script": {"new_purpose": "updated testing"}
    }

    response = client.put(
        f"/employees/{employee_to_update.id}",
        json=updated_data,
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == employee_to_update.id
    assert data["employee_name"] == employee_to_update.employee_name # employee_name NÃO deve mudar
    assert data["ia_name"] == updated_data["ia_name"]
    assert data["endpoint_key"] == updated_data["endpoint_key"]
    assert data["employee_script"] == updated_data["employee_script"]
    assert "last_update" in data # Deve ter um novo last_update

    # Verifique também no banco de dados
    updated_db_employee = db_session_override.query(Employee).filter(Employee.id == employee_to_update.id).first()
    assert updated_db_employee.ia_name == updated_data["ia_name"]
    assert updated_db_employee.endpoint_key == updated_data["endpoint_key"]
    assert updated_db_employee.employee_script == updated_data["employee_script"]

def test_update_employee_name_is_ignored(client: TestClient, db_session_override: Session):
    """
    Testa se a tentativa de atualizar 'employee_name' é IGNORADA e retorna 200.
    A validação do schema permite o campo, mas o CRUD o ignora.
    """
    admin_password = "AdminEmployeeNoNameChange!"
    admin_user = create_test_admin_user(db_session_override, "admin_employee_no_name_change", admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_user.username, admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    employee_to_update = create_test_employee(db_session_override, "Original Name", ia_name="InitialIA")

    updated_data_with_ignored_field = {
        "employee_name": "New Forbidden Name", # Este campo deve ser ignorado pelo CRUD
        "ia_name": "UpdatedIA" # Este campo deve ser atualizado
    }

    response = client.put(
        f"/employees/{employee_to_update.id}",
        json=updated_data_with_ignored_field,
        headers=headers
    )
    
    # Agora esperamos 200, pois o CRUD lida com isso.
    assert response.status_code == 200
    data = response.json()
    assert data["employee_name"] == "Original Name" # Confirma que não foi alterado na resposta
    assert data["ia_name"] == "UpdatedIA" # Confirma que outro campo foi atualizado

    # Verifique no banco de dados que o nome NÃO foi alterado e outros campos foram.
    db_employee_after_attempt = db_session_override.query(Employee).filter(Employee.id == employee_to_update.id).first()
    assert db_employee_after_attempt.employee_name == "Original Name"
    assert db_employee_after_attempt.ia_name == "UpdatedIA"


def test_update_employee_not_found_as_admin(client: TestClient, db_session_override: Session):
    """
    Testa se a atualização de um funcionário não encontrado retorna 404.
    """
    admin_password = "AdminEmployeeUpdateNotFound!"
    admin_user = create_test_admin_user(db_session_override, "admin_employee_update_not_found", admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_user.username, admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    non_existent_id = 99999
    updated_data = {"ia_name": "NonExistentIA"}

    response = client.put(
        f"/employees/{non_existent_id}",
        json=updated_data,
        headers=headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Funcionário não encontrado"