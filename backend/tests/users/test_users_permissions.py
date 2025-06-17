# File: backend/tests/users/test_users_permissions.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Importar as funções auxiliares do conftest.py
from tests.conftest import create_test_user, get_user_token, create_test_admin_user, get_admin_token

# Importar modelos (se necessário para verificações diretas no DB após as requisições)
from src.models.user_models import User
from src.models.admin_user_models import AdminUser


# Teste de leitura do próprio usuário (GET /users/me)
def test_read_own_user_profile(client: TestClient, db_session_override: Session):
    # Senha forte conforme o novo schema UserCreate, com caractere especial
    user_password = "UserReadP@ss1!" # Adicionado '!' para caractere especial
    user_email = "self_read_profile@example.com"
    user_name = "Self Read Profile User"
    user_phone_number = "5511987654321" # Formato válido para Brasil (13 digitos)
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password, phone_number=user_phone_number)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get(f"/users/me", headers=headers)

    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.json()}"
    response_data = response.json()
    assert response_data["id"] == user_credentials.id
    assert response_data["email"] == user_email
    assert response_data["name"] == user_name
    assert response_data["phone_number"] == user_phone_number
    assert "password_hash" not in response_data
    assert "two_factor_secret" not in response_data


# Teste: Atualização do próprio perfil via /users/me (PUT /users/me)
def test_update_own_user_profile_via_me(client: TestClient, db_session_override: Session):
    user_password = "SelfUpdateP@ss1!" # Senha forte
    user_email = "self_update_me@example.com"
    user_name = "Self Update Me User"
    user_phone_number = "5511987654322" # Telefone único
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password, phone_number=user_phone_number)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    updated_data = {
        "name": "Updated Self Name Via Me",
        "phone_number": "5511987654323", # Novo phone_number, ainda 13 dígitos
        "email_verified": True
    }

    response = client.put(f"/users/me", json=updated_data, headers=headers)

    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.json()}"
    response_json = response.json()
    assert response_json["name"] == "Updated Self Name Via Me"
    response_json["phone_number"] == "5511987654323"
    assert response_json["email"] == user_email
    assert response_json["email_verified"] == True

    updated_user_in_db = db_session_override.query(User).filter(User.id == user_credentials.id).first()
    assert updated_user_in_db.name == "Updated Self Name Via Me"
    assert updated_user_in_db.phone_number == "5511987654323"
    assert updated_user_in_db.email_verified == True


# Teste: Um usuário comum NÃO PODE usar a rota /users/{user_id} para se atualizar (espera-se 403 Forbidden)
# Assumindo que PUT /users/{user_id} é uma rota exclusiva para admins, ou que a lógica proíbe self-update via ID explícito
def test_update_user_as_self_via_id_forbidden(client: TestClient, db_session_override: Session):
    user_password = "ForbiddenP@ss1!" # Senha forte
    user_email = "self_update_forbidden@example.com"
    user_phone_number = "5511987654324" # Telefone único
    user_credentials = create_test_user(db_session_override, "User Forbidden Update", user_email, user_password, phone_number=user_phone_number)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    updated_data = {"name": "Should Not Update", "phone_number": "5511000000000"}

    response = client.put(f"/users/{user_credentials.id}", json=updated_data, headers=headers)

    # CORREÇÃO: A rota deveria retornar 403, não 200. Se sua API não implementou isso ainda,
    # você precisará ajustar a API para que um usuário comum não possa atualizar a si mesmo
    # usando a rota /users/{user_id} e sim apenas /users/me.
    # Por enquanto, vamos esperar 403.
    assert response.status_code == 403, f"Expected status 403, got {response.status_code}. Response: {response.json()}"
    assert "Forbidden" in response.json()["detail"] or "Não autorizado" in response.json()["detail"]

    user_in_db = db_session_override.query(User).filter(User.id == user_credentials.id).first()
    assert user_in_db.name == "User Forbidden Update"
    assert user_in_db.phone_number != "5511000000000"


# Teste: Atualizar outro usuário como ADMIN (PUT /users/{user_id})
def test_update_user_as_admin(client: TestClient, db_session_override: Session):
    admin_password = "AdminUpdateP@ss1!" # Senha forte, com caractere especial
    admin_username = "admin_update_user"
    admin_user = create_test_admin_user(db_session_override, admin_username, admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_username, admin_password)

    user_to_update_password = "UserToUpdateP@ss1!" # Senha forte, com caractere especial
    user_to_update_email = "user.to.update@example.com"
    user_to_update_phone_number = "5521912345677" # Telefone único
    user_to_update = create_test_user(db_session_override, "Original Name", user_to_update_email, user_to_update_password, phone_number=user_to_update_phone_number)

    headers = {"Authorization": f"Bearer {admin_token}"}
    updated_data = {
        "name": "Updated by Admin",
        "phone_number": "5521912345678", # Novo phone_number
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


# Teste: Tentar atualizar outro usuário como usuário comum (DEVE FALHAR COM 403 Forbidden)
def test_update_other_user_as_normal_user_forbidden(client: TestClient, db_session_override: Session):
    user_updater_password = "UpdaterP@ss1!" # Senha forte
    user_updater_email = "updater@example.com"
    user_updater_phone_number = "5511987654325"
    user_updater = create_test_user(db_session_override, "User Updater", user_updater_email, user_updater_password, phone_number=user_updater_phone_number)
    user_updater_token = get_user_token(client, db_session_override, email=user_updater.email, password=user_updater_password)

    user_target_password = "TargetP@ss1!" # Senha forte
    user_target_email = "target@example.com"
    user_target_phone_number = "5511987654326"
    user_target = create_test_user(db_session_override, "User Target", user_target_email, user_target_password, phone_number=user_target_phone_number)

    headers = {"Authorization": f"Bearer {user_updater_token}"}
    updated_data = {"name": "Malicious Name Change"}

    response = client.put(f"/users/{user_target.id}", json=updated_data, headers=headers)

    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"] or "Não autorizado" in response.json()["detail"]

    target_user_in_db = db_session_override.query(User).filter(User.id == user_target.id).first()
    assert target_user_in_db.name == "User Target"


# Teste: Atualizar usuário com dados inválidos (ex: email mal formatado ou campo inesperado)
def test_update_user_invalid_data(client: TestClient, db_session_override: Session):
    user_password = "InvalidDataP@ss!" # Senha forte
    user_email = "invalid.data@example.com"
    user_phone_number = "5511987654327"
    user_credentials = create_test_user(db_session_override, "Invalid Data User", user_email, user_password, phone_number=user_phone_number)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    invalid_data = {
        "name": "Still Valid Name",
        "email": "invalid-email", # Email mal formatado
        "extra_field": "should_not_be_here" # Campo inesperado
    }

    response = client.put(f"/users/{user_credentials.id}", json=invalid_data, headers=headers)

    assert response.status_code == 422 # Unprocessable Entity
    response_detail = response.json()["detail"]
    assert any("value is not a valid email address" in error["msg"] for error in response_detail)
    assert any("extra_forbidden" in error["type"] or "field_not_permitted" in error["type"] for error in response_detail)


# Teste: Leitura de usuário não existente por admin (GET /admin/users/{id})
def test_read_non_existent_user_as_admin(client: TestClient, db_session_override: Session):
    admin_password = "AdminReadNoExP@ss!" # Senha forte
    admin_username = "admin_test_read"
    admin_user = create_test_admin_user(db_session_override, admin_username, admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_username, admin_password)

    headers = {"Authorization": f"Bearer {admin_token}"}
    non_existent_id = 9999999

    response = client.get(f"/admin/users/{non_existent_id}", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found" # Ou "Usuário não encontrado"


# Teste para criação de usuário sem dados obrigatórios (via API)
@pytest.mark.parametrize("missing_field", ["name", "password"])
def test_create_user_missing_strictly_required_fields_api(client: TestClient, missing_field: str):
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
    assert any(error["loc"] == ("body", missing_field) and "missing" in error["type"] for error in response.json()["detail"])


# Teste para criação de usuário sem email nem phone_number
def test_create_user_missing_email_and_phone_number_api(client: TestClient):
    invalid_data = {
        "name": "Usuario Sem Contato",
        "password": "SenhaForte123!"
    }
    response = client.post("/users/", json=invalid_data)
    assert response.status_code == 422
    assert any("Pelo menos um email ou um número de telefone deve ser fornecido para o cadastro." in error["msg"] for error in response.json()["detail"])


# Teste: Leitura de usuários como admin (listar todos os usuários) (GET /admin/users/)
def test_read_all_users_as_admin(client: TestClient, db_session_override: Session):
    admin_password = "AdminListP@ss1!" # Senha forte, com caractere especial
    admin_username = "admin_list_users"
    admin_user = create_test_admin_user(db_session_override, admin_username, admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_username, admin_password)

    user1 = create_test_user(db_session_override, "User One", "user1@example.com", "UserOneP@ss1!", phone_number="5511999999901")
    user2 = create_test_user(db_session_override, "User Two", "user2@example.com", "UserTwoP@ss1!", phone_number="5511999999902")

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/admin/users/", headers=headers)

    assert response.status_code == 200
    users_data = response.json()
    # Adicionar asserções para verificar o conteúdo da lista de usuários, por exemplo:
    # assert len(users_data) >= 2 # Pode haver outros usuários criados pelos fixtures
    # assert any(user["email"] == "user1@example.com" for user in users_data)
    # assert any(user["email"] == "user2@example.com" for user in users_data)

# Testes de exclusão (mencionados nos logs, mas não totalmente fornecidos no código)
# test_delete_user_as_admin
# test_delete_non_existent_user_as_admin
# Se existirem, devem ser mantidos pois testam a permissão de admin para exclusão via API.