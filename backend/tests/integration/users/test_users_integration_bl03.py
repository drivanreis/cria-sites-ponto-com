# File: backend/tests/integration/users/test_users_integration_bl03.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status

from src.main import app 
from src.models.user_models import User
from src.cruds import user_cruds
from tests.conftest import db_session_override, client, create_test_user, get_user_token, get_admin_token
from tests.integration.users.data_users_integration import get_valid_manual_user_data, get_valid_social_user_data

# --------- Testes de Criacao Manual -----------

def test_create_manual_user_success(client: TestClient, db_session_override: Session):
    user_data = get_valid_manual_user_data("success")
    response = client.post("/users/", json=user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["nickname"] == user_data["nickname"]
    assert data["id"] is not None

    db_user = db_session_override.query(User).filter(User.email == user_data["email"]).first()
    assert db_user is not None
    assert user_cruds.verify_user_password(db_session_override, db_user.id, user_data["password"])

def test_create_manual_user_duplicate_email(client: TestClient, db_session_override: Session):
    user_data = get_valid_manual_user_data("duplicate_email")
    client.post("/users/", json=user_data)
    
    duplicate_data = get_valid_manual_user_data("other")
    duplicate_data["email"] = user_data["email"]
    response = client.post("/users/", json=duplicate_data)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "Email" in response.json()["detail"]

def test_create_manual_user_duplicate_phone(client: TestClient, db_session_override: Session):
    user_data = get_valid_manual_user_data("duplicate_phone")
    client.post("/users/", json=user_data)

    duplicate_data = get_valid_manual_user_data("other")
    duplicate_data["phone_number"] = user_data["phone_number"]
    response = client.post("/users/", json=duplicate_data)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "telefone" in response.json()["detail"]

@pytest.mark.parametrize("field", ["nickname", "password"])
def test_create_manual_user_missing_required_fields(client: TestClient, field):
    user_data = get_valid_manual_user_data("missing")
    del user_data[field]
    response = client.post("/users/", json=user_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_manual_user_invalid_email_format(client: TestClient):
    user_data = get_valid_manual_user_data("invalid_email")
    user_data["email"] = "invalid-email"
    response = client.post("/users/", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_manual_user_weak_password(client: TestClient):
    user_data = get_valid_manual_user_data("weak_pass")
    user_data["password"] = "short"
    response = client.post("/users/", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# --------- Testes de Criacao via Login Social -----------

def test_create_social_user_google_success(client: TestClient, db_session_override: Session):
    user_data = get_valid_social_user_data("google_success")
    response = client.post("/users/", json={
        "nickname": user_data["nickname"],
        "google_id": user_data["google_id"]
    })

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["google_id"] == user_data["google_id"]
    assert data["nickname"] == user_data["nickname"]
    
    db_user = db_session_override.query(User).filter(User.google_id == user_data["google_id"]).first()
    assert db_user is not None

def test_create_social_user_github_success(client: TestClient, db_session_override: Session):
    user_data = get_valid_social_user_data("github_success")
    response = client.post("/users/", json={
        "nickname": user_data["nickname"],
        "github_id": user_data["github_id"]
    })

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["github_id"] == user_data["github_id"]
    assert data["nickname"] == user_data["nickname"]
    
    db_user = db_session_override.query(User).filter(User.github_id == user_data["github_id"]).first()
    assert db_user is not None

def test_create_social_user_missing_oauth_ids(client: TestClient):
    user_data = {"nickname": "No Social ID"}
    response = client.post("/users/", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# --------- Testes de Leitura -----------

def test_read_own_user_profile(client: TestClient, db_session_override: Session):
    user_data = get_valid_manual_user_data("read_self")
    user = create_test_user(db_session_override, user_data["nickname"], user_data["email"], user_data["password"], phone_number=user_data["phone_number"])
    token = get_user_token(client, db_session_override, user.email, user_data["password"])
    
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user.email