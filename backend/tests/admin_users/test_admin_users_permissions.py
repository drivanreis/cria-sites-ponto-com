# File: backend/tests/admin_users/test_admin_users_permissions.py

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

# Importe as funções auxiliares do conftest.py
# <<< MUDANÇA AQUI: Adicionar create_test_admin_user e get_admin_token
from tests.conftest import create_test_user, get_user_token, create_test_admin_user, get_admin_token

# Teste de criação de admin por usuário comum (deve ser proibido)
@pytest.mark.asyncio
async def test_create_admin_user_as_regular_user_forbidden(client: AsyncClient, db_session_override: Session):
    user_password = "UserCommon123!" # Senha ajustada
    user_credentials = await create_test_user(db_session_override, "Common User", "common.user@example.com", user_password)
    user_token = await get_user_token(client, db_session_override, user_credentials["email"], user_credentials["password"])
    headers = {"Authorization": f"Bearer {user_token['access_token']}"}

    new_admin_data = {
        "username": "forbidden_admin",
        "password": "ForbiddenAd12!" # Senha ajustada
    }
    response = await client.post(
        "/admin_users/",
        json=new_admin_data,
        headers=headers
    )
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Not enough permissions"

# Teste de criação de admin sem token (deve ser não autorizado)
@pytest.mark.asyncio
async def test_create_admin_user_no_token_unauthorized(client: AsyncClient):
    new_admin_data = {
        "username": "no_token_admin",
        "password": "NoTokenSenh1!" # Senha ajustada
    }
    response = await client.post(
        "/admin_users/",
        json=new_admin_data
    )
    assert response.status_code == 401 # Unauthorized
    assert response.json()["detail"] == "Not authenticated"

# Teste de listagem de admins como usuário comum (deve ser proibido)
@pytest.mark.asyncio
async def test_list_admin_users_as_regular_user_forbidden(client: AsyncClient, db_session_override: Session):
    user_password = "ComumList123!" # Senha ajustada
    user_credentials = await create_test_user(db_session_override, "Comum List", "comum_list@example.com", user_password)
    user_token = await get_user_token(client, db_session_override, user_credentials["email"], user_credentials["password"])
    headers = {"Authorization": f"Bearer {user_token['access_token']}"}

    response = await client.get("/admin_users/", headers=headers)
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Not enough permissions"

# Teste de leitura de admin específico por usuário comum (deve ser proibido)
@pytest.mark.asyncio
async def test_read_specific_admin_user_as_regular_user_forbidden(client: AsyncClient, db_session_override: Session):
    user_password = "ComumRead123!" # Senha ajustada
    user_credentials = await create_test_user(db_session_override, "Comum Read", "comum_read@example.com", user_password)
    user_token = await get_user_token(client, db_session_override, user_credentials["email"], user_password)
    headers = {"Authorization": f"Bearer {user_token['access_token']}"}

    # Crie um admin para tentar ler
    target_admin_credentials = await create_test_admin_user(db_session_override, "admin_to_read", "AdminRead123!") # Senha ajustada

    response = await client.get(f"/admin_users/{target_admin_credentials['id']}", headers=headers)
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Not enough permissions"

# Teste de atualização de admin por usuário comum (deve ser proibido)
@pytest.mark.asyncio
async def test_update_admin_user_as_regular_user_forbidden(client: AsyncClient, db_session_override: Session):
    user_password = "ComumUpd123!" # Senha ajustada
    user_credentials = await create_test_user(db_session_override, "Comum Update", "comum_update@example.com", user_password)
    user_token = await get_user_token(client, db_session_override, user_credentials["email"], user_credentials["password"])
    headers = {"Authorization": f"Bearer {user_token['access_token']}"}

    # Crie um admin para tentar atualizar
    target_admin_credentials = await create_test_admin_user(db_session_override, "admin_to_update_perm", "AdminUpd123!") # Senha ajustada

    updated_data = {"username": "forbidden_updated_name"}
    response = await client.put(
        f"/admin_users/{target_admin_credentials['id']}",
        json=updated_data,
        headers=headers
    )
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Not enough permissions"

# Teste de exclusão de admin por usuário comum (deve ser proibido)
@pytest.mark.asyncio
async def test_delete_admin_user_as_regular_user_forbidden(client: AsyncClient, db_session_override: Session):
    user_password = "ComumDel123!" # Senha ajustada
    user_credentials = await create_test_user(db_session_override, "Comum Delete", "comum_delete@example.com", user_password)
    user_token = await get_user_token(client, db_session_override, user_credentials["email"], user_credentials["password"])
    headers = {"Authorization": f"Bearer {user_token['access_token']}"}

    # Crie um admin para tentar deletar
    target_admin_credentials = await create_test_admin_user(db_session_override, "admin_to_delete_perm", "AdminDel123!") # Senha ajustada

    response = await client.delete(f"/admin_users/{target_admin_credentials['id']}", headers=headers)
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Not enough permissions"