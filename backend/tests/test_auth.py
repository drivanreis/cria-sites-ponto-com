import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Importe as funções auxiliares do conftest.py
from tests.conftest import create_test_user, create_test_admin_user

# Teste de login de usuário comum bem-sucedido
def test_user_login_success(client: TestClient, db_session_override: Session):
    user_password = "UserSenha1234!"
    create_test_user(db_session_override, "Login Test User", "login.user@example.com", user_password)

    login_data = {"username": "login.user@example.com", "password": user_password}
    # CORRIGIDO AQUI: A rota de login é /auth/login, não /auth/token
    response = client.post("/auth/login", data=login_data) # <<<<< MUDANÇA AQUI!

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

# Teste de login de administrador bem-sucedido
def test_admin_login_success(client: TestClient, db_session_override: Session):
    admin_password = "AdminSnh123!"
    create_test_admin_user(db_session_override, "login_admin", admin_password)

    login_data = {"username": "login_admin", "password": admin_password}
    # CORRIGIDO AQUI: A rota de login de admin também é /auth/login na rota unificada
    response = client.post("/auth/login", data=login_data) # <<<<< MUDANÇA AQUI!

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

# Teste de login com credenciais inválidas para usuário
def test_user_login_invalid_credentials(client: TestClient):
    login_data = {"username": "nonexistent@example.com", "password": "wrongpassword"}
    # CORRIGIDO AQUI: A rota de login é /auth/login
    response = client.post("/auth/login", data=login_data) # <<<<< MUDANÇA AQUI!
    assert response.status_code == 401
    # CORRIGIDO AQUI: A mensagem de erro em português para credenciais inválidas
    assert response.json()["detail"] == "Credenciais inválidas ou usuário não encontrado." # <<<<< MUDANÇA AQUI!

# Teste de login com credenciais inválidas para administrador
def test_admin_login_invalid_credentials(client: TestClient):
    login_data = {"username": "nonexistent_admin", "password": "wrongpassword"}
    # CORRIGIDO AQUI: A rota de login é /auth/login
    response = client.post("/auth/login", data=login_data) # <<<<< MUDANÇA AQUI!
    assert response.status_code == 401
    # CORRIGIDO AQUI: A mensagem de erro em português para credenciais inválidas
    assert response.json()["detail"] == "Credenciais inválidas ou usuário não encontrado." # <<<<< MUDANÇA AQUI!

# Teste de login de usuário com senha incorreta
def test_user_login_incorrect_password(client: TestClient, db_session_override: Session):
    user_password = "UserSenha1234!"
    create_test_user(db_session_override, "User Pass Test", "user.pass@example.com", user_password)

    login_data = {"username": "user.pass@example.com", "password": "wrong_password"}
    # CORRIGIDO AQUI: A rota de login é /auth/login
    response = client.post("/auth/login", data=login_data) # <<<<< MUDANÇA AQUI!
    assert response.status_code == 401
    # CORRIGIDO AQUI: A mensagem de erro em português para credenciais inválidas
    assert response.json()["detail"] == "Credenciais inválidas ou usuário não encontrado." # <<<<< MUDANÇA AQUI!

# Teste de login de administrador com senha incorreta
def test_admin_login_incorrect_password(client: TestClient, db_session_override: Session):
    admin_password = "AdminSnh123!"
    create_test_admin_user(db_session_override, "Admin Pass Test", admin_password)

    login_data = {"username": "Admin Pass Test", "password": "wrong_password"}
    # CORRIGIDO AQUI: A rota de login é /auth/login
    response = client.post("/auth/login", data=login_data) # <<<<< MUDANÇA AQUI!
    assert response.status_code == 401
    # CORRIGIDO AQUI: A mensagem de erro em português para credenciais inválidas
    assert response.json()["detail"] == "Credenciais inválidas ou usuário não encontrado." # <<<<< MUDANÇA AQUI!

# Teste de acesso a rota protegida sem token
def test_protected_route_no_token(client: TestClient):
    response = client.get("/users/me") # Exemplo de rota protegida
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# Teste de acesso a rota protegida com token inválido
def test_protected_route_invalid_token(client: TestClient):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/users/me", headers=headers) # Exemplo de rota protegida
    assert response.status_code == 401
    # CORRIGIDO AQUI: Asserção para a mensagem em português, como visto no log
    assert response.json()["detail"] == "Não foi possível validar as credenciais" # <<<<< MUDANÇA AQUI!