# File: backend/tests/admin_users/test_admin_users_permissions.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Importe as funções auxiliares do conftest.py
from tests.conftest import create_test_user, get_user_token, create_test_admin_user, get_admin_token

# Teste de criação de admin por usuário comum (deve ser proibido)
def test_create_admin_user_as_regular_user_forbidden(client: TestClient, db_session_override: Session):
    user_password = "UserCommon123!" # Senha ajustada
    user_credentials = create_test_user(db_session_override, "Common User", "common.user@example.com", user_password)
    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password) # Acessar .email diretamente
    headers = {"Authorization": f"Bearer {user_token}"}

    new_admin_data = {
        "username": "forbidden_admin",
        "password": "ForbiddenAd12!" # Senha ajustada
    }

    response = client.post(
        "/admin_users/",
        json=new_admin_data,
        headers=headers
    )
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Operação não permitida. Requer privilégios de administrador."

# Teste de criação de admin sem token (deve ser proibido)
def test_create_admin_user_no_token_forbidden(client: TestClient, db_session_override: Session):
    new_admin_data = {
        "username": "no_token_admin",
        "password": "NoTokenAd12!" # Senha ajustada
    }

    response = client.post(
        "/admin_users/",
        json=new_admin_data
    )
    assert response.status_code == 401 # Unauthorized
    assert response.json()["detail"] == "Not authenticated"

# Teste de listagem de admins por usuário comum (deve ser proibido)
def test_list_admin_users_as_regular_user_forbidden(client: TestClient, db_session_override: Session):
    user_password = "ListUser123!" # Senha ajustada
    user_credentials = create_test_user(db_session_override, "List User", "list.user@example.com", user_password)

    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get("/admin_users/", headers=headers)
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Operação não permitida. Requer privilégios de administrador."

# Teste de leitura de admin específico por usuário comum (deve ser proibido)
def test_read_specific_admin_user_as_regular_user_forbidden(client: TestClient, db_session_override: Session):
    user_password = "ReadUser123!" # Senha ajustada
    user_credentials = create_test_user(db_session_override, "Read User", "read.user@example.com", user_password)

    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)
    headers = {"Authorization": f"Bearer {user_token}"}

    # Crie um admin para tentar ler
    target_admin = create_test_admin_user(db_session_override, "admin_to_read_perm", "AdminRead123!") # Senha ajustada

    response = client.get(f"/admin_users/{target_admin.id}", headers=headers)
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Operação não permitida. Requer privilégios de administrador."

# Teste de atualização de admin por usuário comum (deve ser proibido)
def test_update_admin_user_as_regular_user_forbidden(client: TestClient, db_session_override: Session):
    user_password = "UpdateUser123!" # Senha ajustada
    user_credentials = create_test_user(db_session_override, "Update User", "update.user@example.com", user_password)

    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)
    headers = {"Authorization": f"Bearer {user_token}"}

    # Crie um admin para tentar atualizar
    target_admin = create_test_admin_user(db_session_override, "admin_to_update_perm", "AdminUpd123!") # Senha ajustada

    updated_data = {"username": "forbidden_updated_name"}

    response = client.put(
        f"/admin_users/{target_admin.id}",
        json=updated_data,
        headers=headers
    )
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Operação não permitida. Requer privilégios de administrador."

# Teste de exclusão de admin por usuário comum (deve ser proibido)
def test_delete_admin_user_as_regular_user_forbidden(client: TestClient, db_session_override: Session):
    user_password = "ComumDel123!" # Senha ajustada
    user_credentials = create_test_user(db_session_override, "Comum Delete", "comum_delete@example.com", user_password)

    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)
    headers = {"Authorization": f"Bearer {user_token}"}

    # Crie um admin para tentar deletar
    target_admin = create_test_admin_user(db_session_override, "admin_to_delete_perm", "AdminDel123!") # Senha ajustada

    response = client.delete(f"/admin_users/{target_admin.id}", headers=headers)
    assert response.status_code == 403 # Forbidden
    assert response.json()["detail"] == "Operação não permitida. Requer privilégios de administrador."