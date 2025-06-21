# backend/tests/integration/employees/test_employees_integration_01.py

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from tests.conftest import create_test_user, get_user_token, create_test_admin_user, get_admin_token # Importa funções auxiliares

@pytest.mark.asyncio
async def test_list_employees(async_client: AsyncClient, admin_access_token: str):
    """
    Testa a listagem de funcionários por um administrador.
    """
    response = await async_client.get("/employees/", headers={
        "Authorization": f"Bearer {admin_access_token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Opcional: Adicionar mais asserções se souber o número esperado de funcionários ou a estrutura de um funcionário.

@pytest.mark.asyncio
async def test_create_employee(async_client: AsyncClient, admin_access_token: str):
    """
    Testa a criação de um novo funcionário por um administrador.
    """
    payload = {
        "name": "Test Employee Created", # Nome único para evitar colisões em testes múltiplos
        "endpoint_url": "https://fake.api/endpoint/test-created",
        "endpoint_key": "fake-key-created",
        "headers_template": {},
        "body_template": {},
        "employee_script": {
            "system_prompt": "You are a helpful assistant for creation tests.",
        },
        "ia_name": "OpenAI"
    }
    response = await async_client.post("/employees/", headers={
        "Authorization": f"Bearer {admin_access_token}"
    }, json=payload)
    assert response.status_code == 201 # 201 Created é o esperado para criação bem-sucedida
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["endpoint_url"] == payload["endpoint_url"]
    assert data["ia_name"] == payload["ia_name"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

@pytest.mark.asyncio
async def test_list_employees_unauthenticated_fails(async_client: AsyncClient):
    """
    Testa a tentativa de listar funcionários sem autenticação (deve falhar).
    """
    response = await async_client.get("/employees/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais"

@pytest.mark.asyncio
async def test_list_employees_as_regular_user_fails(async_client: AsyncClient, db_session_override: Session):
    """
    Testa a tentativa de listar funcionários com token de usuário comum (deve falhar com 403 Forbidden).
    """
    user_password = "UserEmployeeP@ss1!"
    user_email = "user_employee_list@example.com"
    create_test_user(db_session_override, "User Employee List", user_email, user_password)
    user_token_data = await get_user_token(async_client, db_session_override, email=user_email, password=user_password)
    user_token = user_token_data # get_user_token já retorna a string do token diretamente

    response = await async_client.get("/employees/", headers={
        "Authorization": f"Bearer {user_token}"
    })
    assert response.status_code == 403
    assert response.json()["detail"] == "Não autorizado. Apenas administradores podem acessar esta funcionalidade."

@pytest.mark.asyncio
async def test_create_employee_unauthenticated_fails(async_client: AsyncClient):
    """
    Testa a tentativa de criar um funcionário sem autenticação (deve falhar).
    """
    payload = {
        "name": "Unauthorized Employee",
        "endpoint_url": "https://fake.api/unauth",
        "endpoint_key": "unauth-key",
        "headers_template": {},
        "body_template": {},
        "employee_script": {
            "system_prompt": "This should not be created.",
        },
        "ia_name": "OpenAI"
    }
    response = await async_client.post("/employees/", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais"

@pytest.mark.asyncio
async def test_create_employee_as_regular_user_fails(async_client: AsyncClient, db_session_override: Session):
    """
    Testa a tentativa de criar um funcionário com token de usuário comum (deve falhar com 403 Forbidden).
    """
    user_password = "UserCreateEmployeeP@ss1!"
    user_email = "user_employee_create@example.com"
    create_test_user(db_session_override, "User Employee Create", user_email, user_password)
    user_token_data = await get_user_token(async_client, db_session_override, email=user_email, password=user_password)
    user_token = user_token_data

    payload = {
        "name": "User Attempt Employee",
        "endpoint_url": "https://fake.api/user-attempt",
        "endpoint_key": "user-attempt-key",
        "headers_template": {},
        "body_template": {},
        "employee_script": {
            "system_prompt": "User should not create this.",
        },
        "ia_name": "OpenAI"
    }
    response = await async_client.post("/employees/", headers={
        "Authorization": f"Bearer {user_token}"
    }, json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "Não autorizado. Apenas administradores podem acessar esta funcionalidade."

@pytest.mark.asyncio
async def test_read_single_employee_successfully(async_client: AsyncClient, admin_access_token: str):
    """
    Testa a leitura de um funcionário específico por ID por um administrador.
    """
    # Primeiro, cria um funcionário para ler
    payload = {
        "name": "Employee to Read",
        "endpoint_url": "https://fake.api/read",
        "endpoint_key": "fake-key-read",
        "headers_template": {},
        "body_template": {},
        "employee_script": {
            "system_prompt": "System prompt for employee to read.",
        },
        "ia_name": "OpenAI"
    }
    create_response = await async_client.post("/employees/", headers={
        "Authorization": f"Bearer {admin_access_token}"
    }, json=payload)
    assert create_response.status_code == 201
    employee_id = create_response.json()["id"]

    # Agora, tenta ler o funcionário
    read_response = await async_client.get(f"/employees/{employee_id}", headers={
        "Authorization": f"Bearer {admin_access_token}"
    })
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["id"] == employee_id
    assert data["name"] == payload["name"]

@pytest.mark.asyncio
async def test_read_single_employee_unauthenticated_fails(async_client: AsyncClient, admin_access_token: str):
    """
    Testa a tentativa de ler um funcionário específico sem autenticação (deve falhar).
    """
    # Primeiro, cria um funcionário para tentar ler sem autenticação
    payload = {
        "name": "Employee Unauth Read",
        "endpoint_url": "https://fake.api/unauth-read",
        "endpoint_key": "fake-key-unauth-read",
        "headers_template": {},
        "body_template": {},
        "employee_script": {
            "system_prompt": "System prompt for unauth read.",
        },
        "ia_name": "OpenAI"
    }
    create_response = await async_client.post("/employees/", headers={
        "Authorization": f"Bearer {admin_access_token}"
    }, json=payload)
    assert create_response.status_code == 201
    employee_id = create_response.json()["id"]

    response = await async_client.get(f"/employees/{employee_id}") # Sem cabeçalho de autorização
    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais"

@pytest.mark.asyncio
async def test_read_single_employee_as_regular_user_fails(async_client: AsyncClient, db_session_override: Session, admin_access_token: str):
    """
    Testa a tentativa de ler um funcionário específico com token de usuário comum (deve falhar com 403 Forbidden).
    """
    # Primeiro, cria um funcionário
    payload = {
        "name": "Employee User Read",
        "endpoint_url": "https://fake.api/user-read",
        "endpoint_key": "fake-key-user-read",
        "headers_template": {},
        "body_template": {},
        "employee_script": {
            "system_prompt": "System prompt for user read.",
        },
        "ia_name": "OpenAI"
    }
    create_response = await async_client.post("/employees/", headers={
        "Authorization": f"Bearer {admin_access_token}"
    }, json=payload)
    assert create_response.status_code == 201
    employee_id = create_response.json()["id"]

    # Cria e loga como usuário comum
    user_password = "UserReadSingleEmployeeP@ss1!"
    user_email = "user_read_single_employee@example.com"
    create_test_user(db_session_override, "User Read Single Employee", user_email, user_password)
    user_token_data = await get_user_token(async_client, db_session_override, email=user_email, password=user_password)
    user_token = user_token_data

    response = await async_client.get(f"/employees/{employee_id}", headers={
        "Authorization": f"Bearer {user_token}"
    })
    assert response.status_code == 403
    assert response.json()["detail"] == "Não autorizado. Apenas administradores podem acessar esta funcionalidade."


@pytest.mark.asyncio
async def test_read_non_existent_employee_fails(async_client: AsyncClient, admin_access_token: str):
    """
    Testa a tentativa de ler um funcionário que não existe por um administrador (deve falhar com 404 Not Found).
    """
    non_existent_employee_id = 999999999 # ID que certamente não existe

    response = await async_client.get(f"/employees/{non_existent_employee_id}", headers={
        "Authorization": f"Bearer {admin_access_token}"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Funcionário não encontrado."