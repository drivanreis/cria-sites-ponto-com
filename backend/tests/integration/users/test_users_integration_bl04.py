# File: backend/tests/integration/users/test_users_integration_bl06.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status

from tests.conftest import create_test_user, get_user_token, create_test_admin_user, get_admin_token
from src.models.user_models import User

# ==========================================
# A - Testes do próprio usuário (leitura e atualização via /me)
# ==========================================

def test_read_own_user_profile(client: TestClient, db_session_override: Session):
    user_password = "UserReadP@ss1!"
    user_email = "self_read_profile@example.com"
    user_name = "Self Read Profile User"
    user_phone_number = "5511987654321"

    user_credentials = create_test_user(
        db_session_override,
        user_name,
        user_email,
        user_password,
        phone_number=user_phone_number
    )
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/users/me", headers=headers)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == user_credentials.id
    assert response_data["email"] == user_email
    assert response_data["nickname"] == user_name
    assert response_data["phone_number"] == user_phone_number
    assert "password_hash" not in response_data
    assert "two_factor_secret" not in response_data

def test_update_own_user_profile_via_me(client: TestClient, db_session_override: Session):
    user_password = "SelfUpdateP@ss1!"
    user_email = "self_update_me@example.com"
    user_name = "Self Update Me User"
    user_phone_number = "5511987654322"

    user_credentials = create_test_user(
        db_session_override,
        user_name,
        user_email,
        user_password,
        phone_number=user_phone_number
    )
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    updated_data = {
        "nickname": "Updated Self Name Via Me",
        "phone_number": "5511987654323"
    }

    response = client.put("/users/me", json=updated_data, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["nickname"] == "Updated Self Name Via Me"
    assert response_json["phone_number"] == "5511987654323"
    assert response_json["email"] == user_email

    updated_user_in_db = db_session_override.query(User).filter(User.id == user_credentials.id).first()
    assert updated_user_in_db.nickname == "Updated Self Name Via Me"
    assert updated_user_in_db.phone_number == "5511987654323"

# ==========================================
# B - Testes de permissão de atualização
# ==========================================

def test_update_user_as_self_via_id_forbidden(client: TestClient, db_session_override: Session):
    user_password = "ForbiddenP@ss1!"
    user_email = "self_update_forbidden@example.com"
    user_phone_number = "5511987654324"

    user_credentials = create_test_user(db_session_override, "User Forbidden Update", user_email, user_password, phone_number=user_phone_number)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    updated_data = {"nickname": "Should Not Update", "phone_number": "5511000000000"}

    response = client.put(f"/users/{user_credentials.id}", json=updated_data, headers=headers)

    assert response.status_code == 403
    assert "Operação não permitida" in response.json()["detail"]

def test_update_other_user_as_normal_user_forbidden(client: TestClient, db_session_override: Session):
    user_updater = create_test_user(db_session_override, "User Updater", "updater@example.com", "UpdaterP@ss1!", phone_number="5511987654325")
    user_updater_token = get_user_token(client, db_session_override, email="updater@example.com", password="UpdaterP@ss1!")

    user_target = create_test_user(db_session_override, "User Target", "target@example.com", "TargetP@ss1!", phone_number="5511987654326")

    headers = {"Authorization": f"Bearer {user_updater_token}"}
    updated_data = {"nickname": "Malicious Name Change"}

    response = client.put(f"/users/{user_target.id}", json=updated_data, headers=headers)

    assert response.status_code == 403
    assert "Operação não permitida" in response.json()["detail"]

# ==========================================
# C - Testes de update por admin
# ==========================================

def test_update_user_as_admin(client: TestClient, db_session_override: Session):
    admin_user = create_test_admin_user(db_session_override, "admin_update_user", "AdminUpdateP@ss1!")
    admin_token = get_admin_token(client, db_session_override, "admin_update_user", "AdminUpdateP@ss1!")

    user_to_update = create_test_user(db_session_override, "Original Name", "user.to.update@example.com", "UserToUpdateP@ss1!", phone_number="5521912345677")

    headers = {"Authorization": f"Bearer {admin_token}"}
    updated_data = {
        "nickname": "Updated by Admin",
        "phone_number": "5521912345678"
    }

    response = client.put(f"/users/{user_to_update.id}", json=updated_data, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["nickname"] == "Updated by Admin"
    assert response_json["phone_number"] == "5521912345678"

# ==========================================
# D - Testes de dados inválidos
# ==========================================

def test_update_user_invalid_data(client: TestClient, db_session_override: Session):
    user_credentials = create_test_user(db_session_override, "Invalid Data User", "invalid.data@example.com", "InvalidDataP@ss1!", phone_number="5511987654327")
    user_token = get_user_token(client, db_session_override, email="invalid.data@example.com", password="InvalidDataP@ss1!")

    headers = {"Authorization": f"Bearer {user_token}"}
    invalid_data = {
        "nickname": "Still Valid Name",
        "email": "invalid-email"
    }

    response = client.put("/users/me", json=invalid_data, headers=headers)

    assert response.status_code == 422
    response_detail = response.json()["detail"]
    assert any("value is not a valid email address" in error["msg"] for error in response_detail)

def test_create_user_missing_email_and_phone_number_api(client: TestClient):
    invalid_data = {
        "nickname": "Usuario Sem Contato",
        "password": "SenhaForte123!"
    }
    response = client.post("/users/", json=invalid_data)
    assert response.status_code == 422

# ==========================================
# F - Testes de leitura admin
# ==========================================

def test_read_non_existent_user_as_admin(client: TestClient, db_session_override: Session):
    admin_user = create_test_admin_user(db_session_override, "admin_test_read", "AdminReadNoExP@ss!")
    admin_token = get_admin_token(client, db_session_override, "admin_test_read", "AdminReadNoExP@ss!")

    headers = {"Authorization": f"Bearer {admin_token}"}
    non_existent_id = 9999999

    response = client.get(f"/admin/users/{non_existent_id}", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] in ["User not found", "Not Found"]

# --- New Tests for bl04 ---

def test_update_own_user_profile_change_password(client: TestClient, db_session_override: Session):
    user_password = "OriginalP@ss1!"
    user_email = "change_pass_user@example.com"
    user_name = "Change Pass User"

    user_credentials = create_test_user(
        db_session_override,
        user_name,
        user_email,
        user_password
    )
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    new_password = "NewStrongP@ss2!"
    updated_data = {
        "password": new_password
    }

    response = client.put("/users/me", json=updated_data, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["email"] == user_email
    # Password hash is not returned in UserRead schema, which is good.

    # Try logging in with the old password (should fail)
    old_password_login = client.post("/auth/login", data={"username": user_email, "password": user_password})
    assert old_password_login.status_code == status.HTTP_401_UNAUTHORIZED

    # Try logging in with the new password (should succeed)
    new_password_login = client.post("/auth/login", data={"username": user_email, "password": new_password})
    assert new_password_login.status_code == status.HTTP_200_OK
    assert "access_token" in new_password_login.json()

def test_update_own_user_profile_clear_optional_fields(client: TestClient, db_session_override: Session):
    user_password = "ClearFieldsP@ss1!"
    user_email = "clear.fields@example.com"
    user_name = "Clear Fields User"
    user_phone_number = "5511987654329"

    user_credentials = create_test_user(
        db_session_override,
        user_name,
        user_email,
        user_password,
        phone_number=user_phone_number
    )
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    updated_data = {
        "phone_number": None # Clear phone number
    }

    response = client.put("/users/me", json=updated_data, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["phone_number"] is None
    assert response_json["email"] == user_email # Email should remain unchanged

    updated_user_in_db = db_session_override.query(User).filter(User.id == user_credentials.id).first()
    assert updated_user_in_db.phone_number is None

def test_admin_update_user_non_existent(client: TestClient, db_session_override: Session):
    admin_user = create_test_admin_user(db_session_override, "admin_update_noexist", "AdminUpdateNoExistP@ss!")
    admin_token = get_admin_token(client, db_session_override, "admin_update_noexist", "AdminUpdateNoExistP@ss!")

    headers = {"Authorization": f"Bearer {admin_token}"}
    non_existent_id = 99999999
    updated_data = {
        "nickname": "Attempted Update"
    }

    response = client.put(f"/users/{non_existent_id}", json=updated_data, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Usuário não encontrado"

def test_admin_delete_non_existent_user(client: TestClient, db_session_override: Session):
    admin_user = create_test_admin_user(db_session_override, "admin_delete_noexist", "AdminDeleteNoExistP@ss!")
    admin_token = get_admin_token(client, db_session_override, "admin_delete_noexist", "AdminDeleteNoExistP@ss!")

    headers = {"Authorization": f"Bearer {admin_token}"}
    non_existent_id = 99999999

    response = client.delete(f"/users/{non_existent_id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Usuário não encontrado"

