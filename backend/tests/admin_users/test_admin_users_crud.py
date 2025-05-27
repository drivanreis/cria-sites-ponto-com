# File: backend/tests/admin_users/test_admin_users_crud.py

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

# Importe as funções auxiliares do conftest.py
from tests.conftest import create_test_admin_user, get_admin_token

# Teste de criação de admin por outro admin
@pytest.mark.asyncio
async def test_create_admin_user_as_admin(client: AsyncClient, db_session_override: Session):
    admin_password = "AdminSnh123!" # Senha ajustada
    admin_token = await get_admin_token(client, db_session_override, "test_admin", admin_password)
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    new_admin_data = {
        "username": "new_admin_user",
        "password": "NewAdminPass12!" # Senha ajustada (máx 16 caracteres)
    }
    response = await client.post(
        "/admin_users/",
        json=new_admin_data,
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == new_admin_data["username"]
    assert "id" in data
    assert "creation_date" in data
    assert "password_hash" not in data

# Teste de listagem de admins como administrador
@pytest.mark.asyncio
async def test_list_admin_users_as_admin(client: AsyncClient, db_session_override: Session):
    admin_password = "ListAdmin123!" # Senha ajustada
    admin_token = await get_admin_token(client, db_session_override, "list_admin", admin_password)
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    # Crie mais um admin para garantir que haja pelo menos dois (o que logou + o criado)
    await create_test_admin_user(db_session_override, "another_admin", "AnotherAdm12!") # Senha ajustada

    response = await client.get("/admin_users/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2 # Deve ter o admin que logou e o "another_admin"
    assert any(admin["username"] == "list_admin" for admin in data)
    assert any(admin["username"] == "another_admin" for admin in data)

# Teste de leitura de admin específico por outro admin
@pytest.mark.asyncio
async def test_read_specific_admin_user_as_admin(client: AsyncClient, db_session_override: Session):
    admin_password = "ReaderAdmi123!" # Senha ajustada
    admin_token = await get_admin_token(client, db_session_override, "reader_admin", admin_password)
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    target_admin_credentials = await create_test_admin_user(db_session_override, "target_admin", "TargetAdm123!") # Senha ajustada

    response = await client.get(f"/admin_users/{target_admin_credentials['id']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == target_admin_credentials["id"]
    assert data["username"] == target_admin_credentials["username"]

# Teste de atualização de admin por outro admin
@pytest.mark.asyncio
async def test_update_admin_user_as_admin(client: AsyncClient, db_session_override: Session):
    admin_password = "UpdaterAdmi123!" # Senha ajustada
    admin_token = await get_admin_token(client, db_session_override, "updater_admin", admin_password)
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    target_admin_credentials = await create_test_admin_user(db_session_override, "admin_to_update", "ToUpdateAd12!") # Senha ajustada

    updated_data = {"username": "updated_admin_name"}
    response = await client.put(
        f"/admin_users/{target_admin_credentials['id']}",
        json=updated_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == target_admin_credentials["id"]
    assert data["username"] == updated_data["username"]

# Teste de exclusão de admin por outro admin
@pytest.mark.asyncio
async def test_delete_admin_user_as_admin(client: AsyncClient, db_session_override: Session):
    admin_password = "DeleterAdmi123!" # Senha ajustada
    admin_token = await get_admin_token(client, db_session_override, "deleter_admin", admin_password)
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    target_admin_credentials = await create_test_admin_user(db_session_override, "admin_to_delete", "ToDeleteAd12!") # Senha ajustada

    response = await client.delete(f"/admin_users/{target_admin_credentials['id']}", headers=headers)
    assert response.status_code == 204 # No Content

    # Tente buscar o admin deletado para confirmar a exclusão
    response = await client.get(f"/admin_users/{target_admin_credentials['id']}", headers=headers)
    assert response.status_code == 404 # Not Found