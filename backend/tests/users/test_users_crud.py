# File: backend/tests/users/test_users_crud.py

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

# Importe as funções auxiliares do conftest.py
from tests.conftest import create_test_user, get_user_token

# Teste de criação de usuário comum
@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    user_data = {
        "name": "Novo Usuário",
        "email": "novo.user@example.com",
        "password": "SenhaSegura123!" # Senha ajustada
    }
    response = await client.post(
        "/users/",
        json=user_data
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "creation_date" in data
    assert "password_hash" not in data # A senha hasheada não deve ser retornada

# Teste de criação de usuário com email duplicado
@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient, db_session_override: Session):
    # Crie um usuário primeiro
    user_password = "Password1234!" # Senha ajustada
    await create_test_user(db_session_override, "Duplicado Teste", "duplicate@example.com", user_password)

    # Tente criar outro usuário com o mesmo email
    duplicate_user_data = {
        "name": "Outro Usuário",
        "email": "duplicate@example.com",
        "password": "OutraSenha123!" # Senha ajustada
    }
    response = await client.post(
        "/users/",
        json=duplicate_user_data
    )
    assert response.status_code == 409 # Conflito
    assert response.json()["detail"] == "Email já registrado"

# Teste de leitura de usuário específico por ele mesmo
@pytest.mark.asyncio
async def test_read_specific_user_as_self(client: AsyncClient, db_session_override: Session):
    user_password = "SelfRead1234!" # Senha ajustada
    user_credentials = await create_test_user(db_session_override, "Self Read", "self_read@example.com", user_password)
    user_token = await get_user_token(client, db_session_override, user_credentials["email"], user_credentials["password"])
    headers = {"Authorization": f"Bearer {user_token['access_token']}"}

    response = await client.get(f"/users/{user_credentials['id']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_credentials["id"]
    assert data["name"] == user_credentials["name"] # O create_test_user retorna email, não name. Ajustar retorno ou verificar pelo email
    assert data["email"] == user_credentials["email"]

# Teste de atualização de usuário por ele mesmo
@pytest.mark.asyncio
async def test_update_user_as_self(client: AsyncClient, db_session_override: Session):
    user_password = "SelfUpdate1234!" # Senha ajustada
    user_credentials = await create_test_user(db_session_override, "Self Update", "self_update@example.com", user_password)
    user_token = await get_user_token(client, db_session_override, user_credentials["email"], user_credentials["password"])
    headers = {"Authorization": f"Bearer {user_token['access_token']}"}

    updated_data = {"name": "Nome Atualizado", "phone_number": "11987654321"}
    response = await client.put(
        f"/users/{user_credentials['id']}",
        json=updated_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_credentials["id"]
    assert data["name"] == updated_data["name"]
    assert data["phone_number"] == updated_data["phone_number"]

# Teste de exclusão de usuário por ele mesmo
@pytest.mark.asyncio
async def test_delete_user_as_self(client: AsyncClient, db_session_override: Session):
    user_password = "SelfDelete1234!" # Senha ajustada
    user_credentials = await create_test_user(db_session_override, "Self Delete", "self_delete@example.com", user_password)
    user_token = await get_user_token(client, db_session_override, user_credentials["email"], user_credentials["password"])
    headers = {"Authorization": f"Bearer {user_token['access_token']}"}

    response = await client.delete(f"/users/{user_credentials['id']}", headers=headers)
    assert response.status_code == 204 # No Content

    # Tente buscar o usuário deletado para confirmar a exclusão
    response = await client.get(f"/users/{user_credentials['id']}", headers=headers)
    assert response.status_code == 404 # Not Found