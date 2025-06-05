# File: backend/tests/admin_users/test_admin_users_crud.py

import pytest
from fastapi.testclient import TestClient 
from sqlalchemy.orm import Session

from tests.conftest import create_test_admin_user, get_admin_token
from src.models.admin_user_models import AdminUser

# Teste de criação de admin por outro ADMIN (qualquer admin pode criar)
def test_create_admin_user_as_admin(client: TestClient, db_session_override: Session):
    # Crie um admin que fará a operação
    creator_admin_username = "creator_admin"
    creator_admin_password = "CreatorAdmin123!"
    create_test_admin_user(db_session_override, creator_admin_username, creator_admin_password)
    
    # Obtenha o token para este admin
    admin_token = get_admin_token(client, db_session_override, creator_admin_username, creator_admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    new_admin_data = {
        "username": "new_admin_user",
        "password": "NewAdminPass12!"
    }
    
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
    
    # Verifique se o admin foi realmente criado no banco de dados
    db_new_admin = db_session_override.query(AdminUser).filter(AdminUser.username == new_admin_data["username"]).first()
    assert db_new_admin is not None
    assert db_new_admin.username == new_admin_data["username"]

# Teste de criação de admin com username duplicado
def test_create_admin_user_duplicate_username(client: TestClient, db_session_override: Session):
    creator_admin_username = "dupe_test_admin"
    creator_admin_password = "DupeTestAdmin123!"
    create_test_admin_user(db_session_override, creator_admin_username, creator_admin_password)
    admin_token = get_admin_token(client, db_session_override, creator_admin_username, creator_admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Crie o primeiro admin
    first_admin_data = {
        "username": "duplicate_admin_user",
        "password": "DupAdminPass12!"
    }
    response_first = client.post("/admin_users/", json=first_admin_data, headers=headers)
    assert response_first.status_code == 201

    # Tente criar outro admin com o mesmo username
    second_admin_data = {
        "username": "duplicate_admin_user", # Username duplicado
        "password": "AnotherPass123!"
    }
    response_second = client.post("/admin_users/", json=second_admin_data, headers=headers)
    assert response_second.status_code == 409
    assert response_second.json()["detail"] == "Nome de usuário já registrado por outro administrador."

# Teste de leitura de lista de admins por um ADMIN
def test_read_admin_users_list_as_admin(client: TestClient, db_session_override: Session):
    list_admin_username = "list_admin_user"
    list_admin_password = "ListAdmin123!"
    list_admin_user = create_test_admin_user(db_session_override, list_admin_username, list_admin_password)
    admin_token = get_admin_token(client, db_session_override, list_admin_username, list_admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Cria alguns outros admins de teste
    create_test_admin_user(db_session_override, "admin_x", "AdminX123!")
    create_test_admin_user(db_session_override, "admin_y", "AdminY123!")

    response = client.get("/admin_users/", headers=headers)
    assert response.status_code == 200
    admins_data = response.json()
    assert isinstance(admins_data, list)
    # Deve haver 3 admins: o list_admin_user + admin_x + admin_y
    assert len(admins_data) == 3 
    # Verifica se os usernames esperados estão na lista
    usernames = {admin["username"] for admin in admins_data}
    assert list_admin_username in usernames
    assert "admin_x" in usernames
    assert "admin_y" in usernames

# Teste de leitura do próprio perfil de admin (usando /admin_users/me)
def test_read_own_admin_user_profile_me(client: TestClient, db_session_override: Session):
    admin_username = "self_read_admin"
    admin_password = "SelfReadAdmin123!"
    admin_user = create_test_admin_user(db_session_override, admin_username, admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_username, admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get(f"/admin_users/me", headers=headers) # Rota /me
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == admin_user.id
    assert data["username"] == admin_username
    assert "password_hash" not in data # Verifica que a senha não é exposta
    assert "two_factor_secret" not in data # Verifica que o segredo 2FA não é exposto


# Teste de leitura do próprio perfil de admin (usando /{id})
def test_read_own_admin_user_profile_by_id(client: TestClient, db_session_override: Session):
    admin_username = "self_read_admin_by_id"
    admin_password = "SelfReadAdminById123!"
    admin_user = create_test_admin_user(db_session_override, admin_username, admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_username, admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get(f"/admin_users/{admin_user.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == admin_user.id
    assert data["username"] == admin_username
    assert "password_hash" not in data # Verifica que a senha não é exposta
    assert "two_factor_secret" not in data # Verifica que o segredo 2FA não é exposto


# Teste de leitura do perfil de outro admin por um ADMIN (AGORA PERMITIDO)
def test_read_other_admin_user_profile_as_admin(client: TestClient, db_session_override: Session):
    reader_admin_username = "reader_admin"
    reader_admin_password = "ReaderAdmin123!"
    create_test_admin_user(db_session_override, reader_admin_username, reader_admin_password)
    reader_admin_token = get_admin_token(client, db_session_override, reader_admin_username, reader_admin_password)
    headers = {"Authorization": f"Bearer {reader_admin_token}"}

    # Cria outro admin para ser lido
    other_admin = create_test_admin_user(db_session_override, "other_admin_to_read", "OtherAdmin123!")

    response = client.get(f"/admin_users/{other_admin.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == other_admin.id
    assert data["username"] == "other_admin_to_read"

# Teste de atualização do próprio perfil de admin
def test_update_own_admin_user_profile(client: TestClient, db_session_override: Session):
    admin_username = "self_update_admin"
    admin_password = "SelfUpdateAdmin123!"
    admin_user = create_test_admin_user(db_session_override, admin_username, admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_username, admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    updated_data = {"username": "self_updated_admin"}
    response = client.put(
        f"/admin_users/{admin_user.id}",
        json=updated_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == admin_user.id
    assert data["username"] == updated_data["username"]

    # Verifique se o admin foi realmente atualizado no banco de dados
    updated_admin_in_db = db_session_override.query(AdminUser).filter(AdminUser.id == admin_user.id).first()
    assert updated_admin_in_db.username == updated_data["username"]


# Teste de atualização de outro admin por um ADMIN (AGORA PERMITIDO)
def test_update_other_admin_user_as_admin(client: TestClient, db_session_override: Session):
    updater_admin_username = "updater_admin"
    updater_admin_password = "UpdaterAdmin123!"
    create_test_admin_user(db_session_override, updater_admin_username, updater_admin_password)
    admin_token = get_admin_token(client, db_session_override, updater_admin_username, updater_admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Cria o admin alvo para ser atualizado
    target_admin = create_test_admin_user(db_session_override, "admin_to_update", "ToUpdateAd12!")

    updated_data = {"username": "updated_admin_name", "is_two_factor_enabled": True}
    response = client.put(
        f"/admin_users/{target_admin.id}",
        json=updated_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == target_admin.id
    assert data["username"] == updated_data["username"]
    assert data["is_two_factor_enabled"] == updated_data["is_two_factor_enabled"]
    
    # Verifique se o admin foi realmente atualizado no banco de dados
    updated_admin_in_db = db_session_override.query(AdminUser).filter(AdminUser.id == target_admin.id).first()
    assert updated_admin_in_db.username == updated_data["username"]
    assert updated_admin_in_db.is_two_factor_enabled == updated_data["is_two_factor_enabled"]


# Teste de exclusão de admin por outro ADMIN (AGORA PERMITIDO)
def test_delete_admin_user_as_admin(client: TestClient, db_session_override: Session):
    deleter_admin_username = "deleter_admin"
    deleter_admin_password = "DeleterAdmin123!"
    create_test_admin_user(db_session_override, deleter_admin_username, deleter_admin_password)
    admin_token = get_admin_token(client, db_session_override, deleter_admin_username, deleter_admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Cria o admin alvo para ser deletado
    target_admin = create_test_admin_user(db_session_override, "admin_to_delete", "ToDeleteAd12!")

    response = client.delete(f"/admin_users/{target_admin.id}", headers=headers)
    assert response.status_code == 204 # No Content para deleção bem-sucedida

    # Verifique se o admin foi realmente deletado do banco de dados
    deleted_admin = db_session_override.query(AdminUser).filter(AdminUser.id == target_admin.id).first()
    assert deleted_admin is None

# Teste de exclusão do próprio perfil por um ADMIN (AGORA PERMITIDO)
def test_admin_can_delete_self(client: TestClient, db_session_override: Session):
    self_delete_admin_username = "self_delete_admin"
    self_delete_admin_password = "SelfDeleteAdmin123!"
    self_delete_admin_user = create_test_admin_user(db_session_override, self_delete_admin_username, self_delete_admin_password)
    admin_token = get_admin_token(client, db_session_override, self_delete_admin_username, self_delete_admin_password)
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(f"/admin_users/{self_delete_admin_user.id}", headers=headers)
    assert response.status_code == 204 # Agora, um admin pode deletar a si mesmo

    # Verifique se o admin foi realmente deletado do banco de dados
    deleted_admin = db_session_override.query(AdminUser).filter(AdminUser.id == self_delete_admin_user.id).first()
    assert deleted_admin is None