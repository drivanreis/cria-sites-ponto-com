# File: backend/tests/integration/users/test_users_integration_bl05.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status

from src.main import app 
from src.models.user_models import User
from src.cruds import user_cruds
from tests.conftest import create_test_user
from tests.integration.users.data_users_integration import get_valid_manual_user_data

# (Blocos anteriores já integrados: criação, leitura, atualização e deleção...)

# --------- Testes de Autenticação -----------

def test_user_login_success(client: TestClient, db_session_override: Session):
    user_data = get_valid_manual_user_data("login_success")
    create_test_user(db_session_override, user_data["nickname"], user_data["email"], user_data["password"], phone_number=user_data["phone_number"])

    response = client.post("/auth/login", data={"username": user_data["email"], "password": user_data["password"]})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_user_login_invalid_credentials(client: TestClient):
    response = client.post("/auth/login", data={"username": "nonexistent@example.com", "password": "wrongpass"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_user_login_wrong_password(client: TestClient, db_session_override: Session):
    user_data = get_valid_manual_user_data("wrong_pass")
    create_test_user(db_session_override, user_data["nickname"], user_data["email"], user_data["password"], phone_number=user_data["phone_number"])

    response = client.post("/auth/login", data={"username": user_data["email"], "password": "Invalid123"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_protected_route_no_token(client: TestClient):
    response = client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_protected_route_invalid_token(client: TestClient):
    headers = {"Authorization": "Bearer invalidtoken123"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# --- New Tests for bl03 ---

def test_user_login_with_phone_number_success(client: TestClient, db_session_override: Session):
    user_data = get_valid_manual_user_data("login_with_phone")
    create_test_user(db_session_override, user_data["nickname"], user_data["email"], user_data["password"], phone_number=user_data["phone_number"])

    response = client.post("/auth/login", data={"username": user_data["phone_number"], "password": user_data["password"]})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_user_login_non_existent_email_or_phone(client: TestClient):
    # Try with an email that doesn't exist
    response_email = client.post("/auth/login", data={"username": "nonexistent_id@example.com", "password": "anypassword"})
    assert response_email.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response_email.json()["detail"]

    # Try with a phone number that doesn't exist
    response_phone = client.post("/auth/login", data={"username": "5511900000000", "password": "anypassword"})
    assert response_phone.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response_phone.json()["detail"]
