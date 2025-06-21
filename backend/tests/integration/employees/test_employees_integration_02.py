# backend/tests/integration/employees/test_employees_integration_02.py

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from tests.conftest import create_test_user, get_user_token, create_test_admin_user, get_admin_token # Importa funções auxiliares
from typing import Dict, Any

# fixture to create an employee for tests if not already provided by `test_employee`
# This is a generic test_employee fixture that can be used if no specific one is available in conftest
# If conftest already defines 'test_employee' that creates an employee, this can be omitted or adapted.
@pytest.fixture
async def create_new_employee_for_test(async_client: AsyncClient, admin_access_token: str) -> Dict[str, Any]:
    """Cria um novo funcionário para ser usado em testes."""
    payload = {
        "name": "Employee for CRUD Test",
        "endpoint_url": "https://test.api/employee_crud",
        "endpoint_key": "test-key-crud",
        "headers_template": {},
        "body_template": {},
        "employee_script": {
            "system_prompt": "Prompt para funcionário de teste de CRUD.",
        },
        "ia_name": "OpenAI"
    }
    response = await async_client.post("/employees/", headers={
        "Authorization": f"Bearer {admin_access_token}"
    }, json=payload)
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_get_employee_by_id(async_client: AsyncClient, admin_access_token: str, create_new_employee_for_test: Dict[str, Any]):
    """
    Testa a obtenção de um funcionário por ID.
    Utiliza create_new_employee_for_test para garantir que há um funcionário para buscar.
    """
    test_employee_data = create_new_employee_for_test
    response = await async_client.get(f"/employees/{test_employee_data['id']}", headers={
        "Authorization": f"Bearer {admin_access_token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_employee_data["id"]
    assert data["name"] == test_employee_data["name"]

@pytest.mark.asyncio
async def test_update_employee(async_client: AsyncClient, admin_access_token: str, create_new_employee_for_test: Dict[str, Any]):
    """
    Testa a atualização completa de um funcionário por um administrador (PUT).
    """
    test_employee_data = create_new_employee_for_test
    payload = {
        "name": "Updated Employee Name",
        "endpoint_url": "https://updated.api/endpoint",
        "endpoint_key": "updated-key",
        "headers_template": {"X-Custom-Header": "Value"},
        "body_template": {"message": "Hello updated"},
        "employee_script": {
            "system_prompt": "Updated system prompt.",
        },
        "ia_name": "Claude" # Atualiza também o IA name
    }
    response = await async_client.put(f"/employees/{test_employee_data['id']}", headers={
        "Authorization": f"Bearer {admin_access_token}"
    }, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["endpoint_url"] == payload["endpoint_url"]
    assert data["endpoint_key"] == payload["endpoint_key"]
    assert data["headers_template"] == payload["headers_template"]
    assert data["body_template"] == payload["body_template"]
    assert data["employee_script"] == payload["employee_script"]
    assert data["ia_name"] == payload["ia_name"]
    assert data["id"] == test_employee_data["id"]

@pytest.mark.asyncio
async def test_delete_employee(async_client: AsyncClient, admin_access_token: str, create_new_employee_for_test: Dict[str, Any]):
    """
    Testa a exclusão de um funcionário por um administrador.
    """
    test_employee_data = create_new_employee_for_test
    response = await async_client.delete(f"/employees/{test_employee_data['id']}", headers={
        "Authorization": f"Bearer {admin_access_token}"
    })
    assert response.status_code == 204 # No Content

    # Verifica se o funcionário foi realmente excluído
    get_response = await async_client.get(f"/employees/{test_employee_data['id']}", headers={
        "Authorization": f"Bearer {admin_access_token}"
    })
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Funcionário não encontrado."

@pytest.mark.asyncio
async def test_update_employee_unauthenticated_fails(async_client: AsyncClient, create_new_employee_for_test: Dict[str, Any]):
    """
    Testa a tentativa de atualizar um funcionário sem autenticação (deve falhar).
    """
    test_employee_data = create_new_employee_for_test
    payload = {"name": "Unauthenticated Update"}
    response = await async_client.put(f"/employees/{test_employee_data['id']}", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais"

@pytest.mark.asyncio
async def test_update_employee_as_regular_user_fails(async_client: AsyncClient, db_session_override: Session, create_new_employee_for_test: Dict[str, Any]):
    """
    Testa a tentativa de atualizar um funcionário com token de usuário comum (deve falhar com 403 Forbidden).
    """
    test_employee_data = create_new_employee_for_test
    user_password = "UserUpdateEmployeeP@ss1!"
    user_email = "user_update_employee@example.com"
    create_test_user(db_session_override, "User Update Employee", user_email, user_password)
    user_token_data = await get_user_token(async_client, db_session_override, email=user_email, password=user_password)
    user_token = user_token_data

    payload = {"name": "User Attempt Update"}
    response = await async_client.put(f"/employees/{test_employee_data['id']}", headers={
        "Authorization": f"Bearer {user_token}"
    }, json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "Não autorizado. Apenas administradores podem acessar esta funcionalidade."

@pytest.mark.asyncio
async def test_update_non_existent_employee_fails(async_client: AsyncClient, admin_access_token: str):
    """
    Testa a tentativa de atualizar um funcionário que não existe (deve falhar com 404 Not Found).
    """
    non_existent_employee_id = 999999998
    payload = {"name": "Non Existent Update"}
    response = await async_client.put(f"/employees/{non_existent_employee_id}", headers={
        "Authorization": f"Bearer {admin_access_token}"
    }, json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Funcionário não encontrado."

@pytest.mark.asyncio
async def test_delete_employee_unauthenticated_fails(async_client: AsyncClient, create_new_employee_for_test: Dict[str, Any]):
    """
    Testa a tentativa de deletar um funcionário sem autenticação (deve falhar).
    """
    test_employee_data = create_new_employee_for_test
    response = await async_client.delete(f"/employees/{test_employee_data['id']}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais"

@pytest.mark.asyncio
async def test_delete_employee_as_regular_user_fails(async_client: AsyncClient, db_session_override: Session, create_new_employee_for_test: Dict[str, Any]):
    """
    Testa a tentativa de deletar um funcionário com token de usuário comum (deve falhar com 403 Forbidden).
    """
    test_employee_data = create_new_employee_for_test
    user_password = "UserDeleteEmployeeP@ss1!"
    user_email = "user_delete_employee@example.com"
    create_test_user(db_session_override, "User Delete Employee", user_email, user_password)
    user_token_data = await get_user_token(async_client, db_session_override, email=user_email, password=user_password)
    user_token = user_token_data

    response = await async_client.delete(f"/employees/{test_employee_data['id']}", headers={
        "Authorization": f"Bearer {user_token}"
    })
    assert response.status_code == 403
    assert response.json()["detail"] == "Não autorizado. Apenas administradores podem acessar esta funcionalidade."

@pytest.mark.asyncio
async def test_delete_non_existent_employee_fails(async_client: AsyncClient, admin_access_token: str):
    """
    Testa a tentativa de deletar um funcionário que não existe (deve falhar com 404 Not Found).
    """
    non_existent_employee_id = 999999997
    response = await async_client.delete(f"/employees/{non_existent_employee_id}", headers={
        "Authorization": f"Bearer {admin_access_token}"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Funcionário não encontrado."

@pytest.mark.asyncio
async def test_patch_employee_partial_update(async_client: AsyncClient, admin_access_token: str, create_new_employee_for_test: Dict[str, Any]):
    """
    Testa a atualização parcial de um funcionário (PATCH) por um administrador.
    Assume que o endpoint suporta PATCH para atualização parcial.
    """
    test_employee_data = create_new_employee_for_test
    original_name = test_employee_data["name"]
    original_endpoint_url = test_employee_data["endpoint_url"]

    # Atualiza apenas o nome e o system_prompt
    partial_payload = {
        "name": "Employee Partially Updated",
        "employee_script": {
            "system_prompt": "New partial system prompt.",
        }
    }
    response = await async_client.patch(f"/employees/{test_employee_data['id']}", headers={
        "Authorization": f"Bearer {admin_access_token}"
    }, json=partial_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_employee_data["id"]
    assert data["name"] == partial_payload["name"]
    assert data["employee_script"]["system_prompt"] == partial_payload["employee_script"]["system_prompt"]
    # Verifica se os outros campos não foram alterados
    assert data["endpoint_url"] == original_endpoint_url
    assert data["ia_name"] == test_employee_data["ia_name"]