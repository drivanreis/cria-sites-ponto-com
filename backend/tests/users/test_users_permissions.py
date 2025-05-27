# File: backend/tests/users/test_users_permissions.py

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

# Importe as funções auxiliares do conftest.py
from tests.conftest import create_test_user, create_test_admin_user, get_user_token, get_admin_token

# Teste de listagem de usuários como administrador
@pytest.mark.asyncio
async def test_list_users_as_admin(client: AsyncClient, db_session_override: Session):
    admin_password = "AdListUser123!" # Senha ajustada
    admin_token = await get_admin_token(client, db_session_override, "list_users_admin", admin_password)
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    # Crie alguns usuários para listar
    await create_test_user(db_session_override, "User1", "user1@example.com", "User1Pass123!")
    await create_test_user(db_session_override, "User2", "user2@example.com", "User2Pass123!")

    response = await client.get("/users/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2 # Pode haver mais se outros testes criaram usuários e não limparm
    assert any(user["email"] == "user1@example.com" for user in data)
    assert any(user["email"] == "user2@example.com" for user in data)

# Teste de listagem de usuários como usuário comum (deve ser proibido)
@pytest.mark.asyncio
async def test_list_users_as_regular_user_forbidden(client: AsyncClient, db_session_override: Session):
    user_password = "Forbidden1234!" # Senha ajustada
    user_credentials = await create_test_user(db_session_override, "List Forbidden", "list_forbidden@example.com", user_password)
    user_token = await get_user_token(client, db_session_override, user_credentials["email"], user_credentials["password"])
    headers = {"Authorization": f"Bearer {user_token['access_token']}"}

    response = await client.get("/users/", headers=headers)
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Not enough permissions"

# Teste de leitura de usuário específico por outro usuário (deve ser proibido)
@pytest.mark.asyncio
async def test_read_specific_user_as_other_user_forbidden(client: AsyncClient, db_session_override: Session):
    user_a_password = "UserA1234!" # Senha ajustada
    user_a_credentials = await create_test_user(db_session_override, "User A", "user_a_read@example.com", user_a_password)
    user_a_token = await get_user_token(client, db_session_override, user_a_credentials["email"], user_a_password)
    headers_a = {"Authorization": f"Bearer {user_a_token['access_token']}"}

    user_b_password = "UserB1234!" # Senha ajustada
    user_b_credentials = await create_test_user(db_session_override, "User B", "user_b_read@example.com", user_b_password)

    response = await client.get(f"/users/{user_b_credentials['id']}", headers=headers_a)
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Not enough permissions"

# Teste de leitura de usuário específico como administrador
@pytest.mark.asyncio
async def test_read_specific_user_as_admin(client: AsyncClient, db_session_override: Session):
    admin_password = "AdReadUser123!" # Senha ajustada
    admin_token = await get_admin_token(client, db_session_override, "admin_read_user", admin_password)
    headers_admin = {"Authorization": f"Bearer {admin_token['access_token']}"}

    target_user_password = "TargetUser1234!" # Senha ajustada
    target_user_credentials = await create_test_user(db_session_override, "Target User", "target_user@example.com", target_user_password)

    response = await client.get(f"/users/{target_user_credentials['id']}", headers=headers_admin)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == target_user_credentials["id"]
    assert data["email"] == target_user_credentials["email"]

# Teste de atualização de usuário por outro usuário (deve ser proibido)
@pytest.mark.asyncio
async def test_update_user_as_other_user_forbidden(client: AsyncClient, db_session_override: Session):
    user_a_password = "UserAUpdate1234!" # Senha ajustada
    user_a_credentials = await create_test_user(db_session_override, "User A Update", "user_a_update@example.com", user_a_password)
    user_a_token = await get_user_token(client, db_session_override, user_a_credentials["email"], user_a_password)
    headers_a = {"Authorization": f"Bearer {user_a_token['access_token']}"}

    user_b_password = "UserBUpdate1234!" # Senha ajustada
    user_b_credentials = await create_test_user(db_session_override, "User B Update", "user_b_update@example.com", user_b_password)

    updated_data = {"name": "Nome Proibido"}
    response = await client.put(
        f"/users/{user_b_credentials['id']}",
        json=updated_data,
        headers=headers_a
    )
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Not enough permissions"

# Teste de atualização de usuário como administrador
@pytest.mark.asyncio
async def test_update_user_as_admin(client: AsyncClient, db_session_override: Session):
    admin_password = "AdUpdUser123!" # Senha ajustada
    admin_token = await get_admin_token(client, db_session_override, "admin_update_user", admin_password)
    headers_admin = {"Authorization": f"Bearer {admin_token['access_token']}"}

    target_user_password = "UserToUpdate1234!" # Senha ajustada
    target_user_credentials = await create_test_user(db_session_override, "User To Update", "user_to_update@example.com", target_user_password) # <<< CORRIGIDO EMAIL

    updated_data = {"name": "Nome Atualizado pelo Admin", "phone_number": "99988776655"}
    response = await client.put(
        f"/users/{target_user_credentials['id']}",
        json=updated_data,
        headers=headers_admin
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == target_user_credentials["id"]
    assert data["name"] == updated_data["name"]
    assert data["phone_number"] == updated_data["phone_number"]

# Teste de exclusão de usuário por outro usuário (deve ser proibido)
@pytest.mark.asyncio
async def test_delete_user_as_other_user_forbidden(client: AsyncClient, db_session_override: Session):
    user_a_password = "UserADelete1234!" # Senha ajustada
    user_a_credentials = await create_test_user(db_session_override, "User A Delete", "user_a_delete@example.com", user_a_password)
    user_a_token = await get_user_token(client, db_session_override, user_a_credentials["email"], user_a_password)
    headers_a = {"Authorization": f"Bearer {user_a_token['access_token']}"}

    user_b_password = "UserBDelete1234!" # Senha ajustada
    user_b_credentials = await create_test_user(db_session_override, "User B Delete", "user_b_delete@example.com", user_b_password)

    response = await client.delete(f"/users/{user_b_credentials['id']}", headers=headers_a)
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Not enough permissions"

# Teste de exclusão de usuário como administrador
@pytest.mark.asyncio
async def test_delete_user_as_admin(client: AsyncClient, db_session_override: Session):
    admin_password = "AdDelUser123!" # Senha ajustada
    admin_token = await get_admin_token(client, db_session_override, "admin_delete_user", admin_password)
    headers_admin = {"Authorization": f"Bearer {admin_token['access_token']}"}

    target_user_password = "UserToDelete1234!" # Senha ajustada
    target_user_credentials = await create_test_user(db_session_override, "User To Delete", "user_to_delete@example.com", target_user_password)

    response = await client.delete(f"/users/{target_user_credentials['id']}", headers=headers_admin)
    assert response.status_code == 204 # No Content

    # Tente buscar o usuário deletado para confirmar a exclusão
    response = await client.get(f"/users/{target_user_credentials['id']}", headers=headers_admin)
    assert response.status_code == 404 # Not Found