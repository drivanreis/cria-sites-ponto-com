# File: backend/tests/integration/users/test_users_integration_bl02.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status

from src.main import app 
from src.models.user_models import User
from src.cruds import user_cruds
from tests.conftest import create_test_user, get_user_token
from tests.integration.users.data_users_integration import get_valid_manual_user_data, get_valid_social_user_data

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

def test_read_own_user_profile(client: TestClient, db_session_override: Session):
    user_data = get_valid_manual_user_data("read_self")
    user = create_test_user(db_session_override, user_data["nickname"], user_data["email"], user_data["password"], phone_number=user_data["phone_number"])
    token = get_user_token(client, db_session_override, user.email, user_data["password"])
    
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user.email

# --- New Tests for bl02 ---

def test_create_social_user_github_with_email_success(client: TestClient, db_session_override: Session):
    user_data = {
        "nickname": "GitHubUserWithEmail",
        "email": "github.email@example.com",
        "github_id": "github_id_98765_with_email"
    }
    response = client.post("/users/", json=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["github_id"] == user_data["github_id"]
    assert data["email"] == user_data["email"]
    assert data["nickname"] == user_data["nickname"]
    
    db_user = db_session_override.query(User).filter(User.github_id == user_data["github_id"]).first()
    assert db_user is not None
    assert db_user.email == user_data["email"]

def test_read_own_user_profile_social_login(client: TestClient, db_session_override: Session):
    # This test assumes a social user can still obtain an access token through your auth flow
    # For simplicity, we'll create a user with a password for token generation in this test.
    # In a real scenario, social login would have its own token generation mechanism.
    user_data = get_valid_social_user_data("social_read_self")
    user_password = "SocialLoginP@ss1!" # Added for token generation in test
    user = create_test_user(db_session_override, user_data["nickname"], user_data["email"], user_password, google_id=user_data["google_id"])
    token = get_user_token(client, db_session_override, user.email, user_password)
    
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user.email
    assert data["google_id"] == user_data["google_id"]
    assert data["nickname"] == user_data["nickname"]
