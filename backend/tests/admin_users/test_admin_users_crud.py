# File: backend/tests/admin_users/test_admin_users_crud.py

import pytest
from fastapi.testclient import TestClient 
from sqlalchemy.orm import Session

from tests.conftest import create_test_admin_user, get_admin_token
from src.models.admin_user import AdminUser

# Teste de criação de admin por outro admin
def test_create_admin_user_as_admin(client: TestClient, db_session_override: Session):
    admin_password = "AdminSnh123!" # Senha ajustada
    # Garante que o admin que fará a requisição exista
    _ = create_test_admin_user(db_session_override, "test_admin", admin_password) 
    # Removido await
    admin_token = get_admin_token(client, db_session_override, "test_admin", admin_password) 
    headers = {"Authorization": f"Bearer {admin_token}"} # Usar o token diretamente

    new_admin_data = {
        "username": "new_admin_user",
        "password": "NewAdminPass12!" # Senha ajustada (máx 16 caracteres)
    }
    # Removido await
    response = client.post(
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
# Removido @pytest.mark.asyncio e alterado para TestClient
def test_list_admin_users_as_admin(client: TestClient, db_session_override: Session):
    admin_password = "ListAdmin123!" # Senha ajustada
    # Garante que o admin que fará a requisição exista
    _ = create_test_admin_user(db_session_override, "list_admin", admin_password)
    # Removido await
    admin_token = get_admin_token(client, db_session_override, "list_admin", admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Crie alguns admins de teste
    create_test_admin_user(db_session_override, "admin1", "AdminOne123!")
    create_test_admin_user(db_session_override, "admin2", "AdminTwo123!")

    # Removido await
    response = client.get("/admin_users/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    # Verifica se há pelo menos o admin de teste e os recém-criados
    assert len(data) >= 3 
    assert any(admin["username"] == "admin1" for admin in data)
    assert any(admin["username"] == "admin2" for admin in data)
    assert "password_hash" not in data[0] # Garante que hashes de senha não são expostos

# Teste de leitura de admin específico como administrador
# Removido @pytest.mark.asyncio e alterado para TestClient
def test_read_specific_admin_user_as_admin(client: TestClient, db_session_override: Session):
    admin_password = "ReadAdmin123!" # Senha ajustada
    # Garante que o admin que fará a requisição exista
    _ = create_test_admin_user(db_session_override, "reader_admin", admin_password)
    # Removido await
    admin_token = get_admin_token(client, db_session_override, "reader_admin", admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Cria um admin alvo para ser lido
    target_admin = create_test_admin_user(db_session_override, "admin_to_read", "ToReadAdmin123!") # Senha ajustada

    # Removido await
    response = client.get(f"/admin_users/{target_admin.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == target_admin.id
    assert data["username"] == target_admin.username
    assert "password_hash" not in data

# Teste de atualização de admin por outro admin
# Removido @pytest.mark.asyncio e alterado para TestClient
def test_update_admin_user_as_admin(client: TestClient, db_session_override: Session):
    admin_password = "UpdaterAdmi123!" # Senha ajustada
    # Garante que o admin que fará a requisição exista
    _ = create_test_admin_user(db_session_override, "updater_admin", admin_password)
    # Removido await
    admin_token = get_admin_token(client, db_session_override, "updater_admin", admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    target_admin = create_test_admin_user(db_session_override, "admin_to_update", "ToUpdateAd12!") # Senha ajustada

    updated_data = {"username": "updated_admin_name"}
    # Removido await
    response = client.put(
        f"/admin_users/{target_admin.id}",
        json=updated_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == target_admin.id
    assert data["username"] == updated_data["username"]

# Teste de exclusão de admin por outro admin
# Removido @pytest.mark.asyncio e alterado para TestClient
def test_delete_admin_user_as_admin(client: TestClient, db_session_override: Session):
    admin_password = "DeleterAdmi123!" # Senha ajustada
    # Garante que o admin que fará a requisição exista
    _ = create_test_admin_user(db_session_override, "deleter_admin", admin_password)
    # Removido await
    admin_token = get_admin_token(client, db_session_override, "deleter_admin", admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"} # Usar o token diretamente

    # Cria o admin alvo para ser deletado
    target_admin = create_test_admin_user(db_session_override, "admin_to_delete", "ToDeleteAd12!") # Senha ajustada

    # Removido await
    response = client.delete(f"/admin_users/{target_admin.id}", headers=headers)
    assert response.status_code == 204 # No Content
    
    # Verifica se o admin foi realmente deletado
    deleted_admin = db_session_override.query(AdminUser).filter(AdminUser.id == target_admin.id).first()
    assert deleted_admin is None