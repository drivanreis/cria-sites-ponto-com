# File: backend/tests/users/test_users_permissions.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Importar as funções auxiliares do conftest.py
from tests.conftest import create_test_user, get_user_token, create_test_admin_user, get_admin_token

# Importar modelos (se necessário para verificações diretas no DB após as requisições)
from src.models.user_models import User


# Teste de leitura do próprio usuário (GET /users/me)
def test_read_own_user_profile(client: TestClient, db_session_override: Session):
    user_password = "SelfRead1234!"
    user_email = "self_read_profile@example.com"
    user_name = "Self Read Profile User"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get(f"/users/me", headers=headers)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == user_credentials.id
    assert response_data["email"] == user_email
    assert response_data["name"] == user_name
    assert "password_hash" not in response_data # Garante que o hash da senha não é retornado
    assert "two_factor_secret" not in response_data # Garante que o segredo 2FA não é retornado

# Teste: Atualização do próprio perfil via /users/me (PUT /users/me)
def test_update_own_user_profile_via_me(client: TestClient, db_session_override: Session):
    user_password = "SelfUpdate1234!"
    user_email = "self_update_me@example.com"
    user_name = "Self Update Me User"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    updated_data = {
        "name": "Updated Self Name Via Me",
        "phone_number": "5511987654321",
        "email_verified": True 
    } 

    response = client.put(f"/users/me", json=updated_data, headers=headers)

    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.json()}"
    response_json = response.json()
    assert response_json["name"] == "Updated Self Name Via Me"
    assert response_json["phone_number"] == "5511987654321"
    assert response_json["email"] == user_email 
    assert response_json["email_verified"] == True

    # Verificar se o usuário foi realmente atualizado no banco de dados
    updated_user_in_db = db_session_override.query(User).filter(User.id == user_credentials.id).first()
    assert updated_user_in_db.name == "Updated Self Name Via Me"
    assert updated_user_in_db.phone_number == "5511987654321"
    assert updated_user_in_db.email_verified == True


# Teste: Um usuário comum NÃO PODE usar a rota /users/{user_id} para se atualizar (espera-se 403 Forbidden)
def test_update_user_as_self_via_id_forbidden(client: TestClient, db_session_override: Session):
    user_password = "SelfUpdateForbidden!"
    user_email = "self_update_forbidden@example.com"
    user_credentials = create_test_user(db_session_override, "User Forbidden Update", user_email, user_password)
    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    updated_data = {"name": "Should Not Update", "phone_number": "5511000000000"}

    response = client.put(f"/users/{user_credentials.id}", json=updated_data, headers=headers)

    assert response.status_code == 403, f"Expected status 403, got {response.status_code}. Response: {response.json()}"
    assert "Forbidden" in response.json()["detail"] or "Não autorizado" in response.json()["detail"]

    user_in_db = db_session_override.query(User).filter(User.id == user_credentials.id).first()
    assert user_in_db.name == "User Forbidden Update"
    assert user_in_db.phone_number != "5511000000000"


# Teste: Atualizar outro usuário como ADMIN (PUT /users/{user_id})
def test_update_user_as_admin(client: TestClient, db_session_override: Session):
    admin_password = "AdminUpdate123!"
    admin_username = "admin_update_user"
    admin_user = create_test_admin_user(db_session_override, admin_username, admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_username, admin_password)

    user_to_update_password = "UserToUpdatePass!"
    user_to_update_email = "user.to.update@example.com"
    user_to_update = create_test_user(db_session_override, "Original Name", user_to_update_email, user_to_update_password)

    headers = {"Authorization": f"Bearer {admin_token}"}
    updated_data = {
        "name": "Updated by Admin",
        "phone_number": "5521912345678",
        "status": "blocked" 
    }

    response = client.put(f"/users/{user_to_update.id}", json=updated_data, headers=headers)

    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.json()}"
    response_json = response.json()
    assert response_json["name"] == "Updated by Admin"
    assert response_json["phone_number"] == "5521912345678"
    assert response_json["status"] == "blocked"

    updated_user_in_db = db_session_override.query(User).filter(User.id == user_to_update.id).first()
    assert updated_user_in_db.name == "Updated by Admin"
    assert updated_user_in_db.phone_number == "5521912345678"
    assert updated_user_in_db.status == "blocked"


# Teste para criação de usuário com número de telefone já registrado (via API)
def test_create_user_duplicate_phone_number_api(client: TestClient, db_session_override: Session):
    user_data_initial = {
        "name": "Usuario Telefone Original API",
        "email": "telefone.original.api@example.com",
        "password": "SenhaTeste123!",
        "phone_number": "5511998877665"
    }
    response_initial = client.post("/users/", json=user_data_initial)
    assert response_initial.status_code == 201

    duplicate_phone_data = {
        "name": "Usuario Telefone Duplicado API",
        "email": "telefone.duplicado.api@example.com",
        "password": "OutraSenha123!",
        "phone_number": "5511998877665"
    }
    response_duplicate = client.post("/users/", json=duplicate_phone_data)
    assert response_duplicate.status_code == 409
    assert response_duplicate.json()["detail"] == "Número de telefone já registrado por outro usuário."


# Teste: Tentar atualizar outro usuário como usuário comum (DEVE FALHAR COM 403 Forbidden)
def test_update_other_user_as_normal_user_forbidden(client: TestClient, db_session_override: Session):
    user_updater_password = "UpdaterPass!"
    user_updater_email = "updater@example.com"
    user_updater = create_test_user(db_session_override, "User Updater", user_updater_email, user_updater_password)
    user_updater_token = get_user_token(client, db_session_override, user_updater.email, user_updater_password)

    user_target_password = "TargetPass!"
    user_target_email = "target@example.com"
    user_target = create_test_user(db_session_override, "User Target", user_target_email, user_target_password)

    headers = {"Authorization": f"Bearer {user_updater_token}"}
    updated_data = {"name": "Malicious Name Change"}

    response = client.put(f"/users/{user_target.id}", json=updated_data, headers=headers)

    assert response.status_code == 403 
    assert "Forbidden" in response.json()["detail"] or "Não autorizado" in response.json()["detail"]

    target_user_in_db = db_session_override.query(User).filter(User.id == user_target.id).first()
    assert target_user_in_db.name == "User Target"


# Teste: Atualizar usuário com dados inválidos (ex: email mal formatado ou campo inesperado)
def test_update_user_invalid_data(client: TestClient, db_session_override: Session):
    user_password = "InvalidDataPass!"
    user_email = "invalid.data@example.com"
    user_credentials = create_test_user(db_session_override, "Invalid Data User", user_email, user_password)
    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    invalid_data = {
        "name": "Still Valid Name",
        "email": "invalid-email", 
        "extra_field": "should_not_be_here" 
    }

    response = client.put(f"/users/{user_credentials.id}", json=invalid_data, headers=headers)

    assert response.status_code == 422 
    response_detail = response.json()["detail"]
    assert any("value is not a valid email address" in error["msg"] for error in response_detail)
    assert any("extra_field" in error["loc"] for error in response_detail)


# Teste: Leitura de usuário não existente por admin (GET /admin/users/{id})
def test_read_non_existent_user_as_admin(client: TestClient, db_session_override: Session):
    admin_password = "AdminPass123!"
    admin_username = "admin_test_read"
    admin_user = create_test_admin_user(db_session_override, admin_username, admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_username, admin_password)

    headers = {"Authorization": f"Bearer {admin_token}"}
    non_existent_id = 9999999 

    response = client.get(f"/admin/users/{non_existent_id}", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found" 


# Teste: Criação de usuário com email já registrado (via API)
def test_create_user_duplicate_email_api(client: TestClient, db_session_override: Session):
    user_data_initial = {
        "name": "User Email Original API",
        "email": "email.original.api@example.com",
        "password": "SenhaOriginal123!",
        "phone_number": "5511111111111"
    }
    response_initial = client.post("/users/", json=user_data_initial)
    assert response_initial.status_code == 201

    duplicate_email_data = {
        "name": "User Email Duplicado API",
        "email": "email.original.api@example.com",
        "password": "OutraSenha123!",
        "phone_number": "5511222222222"
    }
    response_duplicate = client.post("/users/", json=duplicate_email_data)
    assert response_duplicate.status_code == 409
    assert response_duplicate.json()["detail"] == "Email já registrado por outro usuário."


# Teste: Criação de usuário sem dados obrigatórios (via API)
@pytest.mark.parametrize("missing_field", ["name", "email", "password", "phone_number"])
def test_create_user_missing_required_fields_api(client: TestClient, missing_field: str):
    base_user_data = {
        "name": "Usuario Teste",
        "email": "teste_missing@example.com",
        "password": "SenhaForte123!",
        "phone_number": "5511999999999"
    }
    
    invalid_data = base_user_data.copy()
    invalid_data.pop(missing_field)

    response = client.post("/users/", json=invalid_data)
    assert response.status_code == 422 
    assert any(error["loc"] == ("body", missing_field) and error["type"] == "value_error.missing" for error in response.json()["detail"])


# Teste: Leitura de usuários como admin (listar todos os usuários) (GET /admin/users/)
def test_read_all_users_as_admin(client: TestClient, db_session_override: Session):
    admin_password = "AdminListPass!"
    admin_username = "admin_list_users"
    admin_user = create_test_admin_user(db_session_override, admin_username, admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_username, admin_password)

    user1 = create_test_user(db_session_override, "User One", "user1@example.com", "pass1")
    user2 = create_test_user(db_session_override, "User Two", "user2@example.com", "pass2")

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/admin/users/", headers=headers)

    assert response.status_code == 200
    users_data = response.json()
    assert isinstance(users_data, list)
    assert len(users_data) >= 2 
    
    user_emails_in_response = {u["email"] for u in users_data}
    assert user1.email in user_emails_in_response
    assert user2.email in user_emails_in_response


# Teste: Deleção de usuário como admin (DELETE /admin/users/{id})
def test_delete_user_as_admin(client: TestClient, db_session_override: Session):
    admin_password = "AdminDeletePass!"
    admin_username = "admin_delete_user"
    admin_user = create_test_admin_user(db_session_override, admin_username, admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_username, admin_password)

    user_to_delete = create_test_user(db_session_override, "User to Delete", "delete.me@example.com", "DeletePass!")

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(f"/admin/users/{user_to_delete.id}", headers=headers)

    assert response.status_code == 204 # No Content

    deleted_user_in_db = db_session_override.query(User).filter(User.id == user_to_delete.id).first()
    assert deleted_user_in_db is None

# Teste: Deleção de usuário não existente como admin (DELETE /admin/users/{id})
def test_delete_non_existent_user_as_admin(client: TestClient, db_session_override: Session):
    admin_password = "AdminDeleteNonExistent!"
    admin_username = "admin_delete_non_existent"
    admin_user = create_test_admin_user(db_session_override, admin_username, admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_username, admin_password)

    headers = {"Authorization": f"Bearer {admin_token}"}
    non_existent_id = 9999999 

    response = client.delete(f"/admin/users/{non_existent_id}", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

# Teste: Tentar deletar outro usuário como usuário comum (DEVE FALHAR COM 403 Forbidden)
def test_delete_other_user_as_normal_user_forbidden(client: TestClient, db_session_override: Session):
    user_deleter_password = "DeleterPass!"
    user_deleter_email = "deleter@example.com"
    user_deleter = create_test_user(db_session_override, "User Deleter", user_deleter_email, user_deleter_password)
    user_deleter_token = get_user_token(client, db_session_override, user_deleter.email, user_deleter_password)

    user_target_password = "DeleteTargetPass!"
    user_target_email = "delete.target@example.com"
    user_target = create_test_user(db_session_override, "User Delete Target", user_target_email, user_target_password)

    headers = {"Authorization": f"Bearer {user_deleter_token}"}

    response = client.delete(f"/users/{user_target.id}", headers=headers) 

    assert response.status_code == 403 
    assert "Forbidden" in response.json()["detail"] or "Não autorizado" in response.json()["detail"]

    target_user_in_db = db_session_override.query(User).filter(User.id == user_target.id).first()
    assert target_user_in_db is not None
    assert target_user_in_db.email == user_target_email

# Teste: Deleção do próprio usuário (DELETE /users/me) - CENÁRIO OPCIONAL
def test_delete_self_user_via_me_allowed(client: TestClient, db_session_override: Session):
    user_password = "SelfDeleteMePass!"
    user_email = "self_delete_me@example.com"
    user_to_delete = create_test_user(db_session_override, "User to Self Delete", user_email, user_password)
    user_token = get_user_token(client, db_session_override, user_email, user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.delete(f"/users/me", headers=headers) 

    assert response.status_code == 204 

    deleted_user_in_db = db_session_override.query(User).filter(User.id == user_to_delete.id).first()
    assert deleted_user_in_db is None