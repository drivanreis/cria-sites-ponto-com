# File: backend/tests/integration/users/test_users_integration_bl05.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status

from src.main import app 
from src.models.user_models import User
from src.cruds import user_cruds
from tests.conftest import db_session_override, client, create_test_user, get_user_token, get_admin_token
from tests.integration.users.data_users_integration import get_valid_manual_user_data, get_valid_social_user_data

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
