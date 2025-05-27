# File: backend/tests/test_auth.py

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

# Importe as funções auxiliares do conftest.py
from tests.conftest import create_test_user, create_test_admin_user

# Teste de login de usuário comum bem-sucedido
@pytest.mark.asyncio
async def test_user_login_success(client: AsyncClient, db_session_override: Session):
    user_password = "UserSenha1234!" # Senha ajustada
    await create_test_user(db_session_override, "Login Test User", "login.user@example.com", user_password)

    login_data = {"username": "login.user@example.com", "password": user_password}
    response = await client.post("/auth/token", data=login_data)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

# Teste de login de administrador bem-sucedido
@pytest.mark.asyncio
async def test_admin_login_success(client: AsyncClient, db_session_override: Session):
    admin_password = "AdminSnh123!" # Senha ajustada (máx 16 caracteres)
    await create_test_admin_user(db_session_override, "login_admin", admin_password)

    login_data = {"username": "login_admin", "password": admin_password}
    response = await client.post("/auth/admin/token", data=login_data)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

# Teste de login com credenciais inválidas para usuário
@pytest.mark.asyncio
async def test_user_login_invalid_credentials(client: AsyncClient):
    login_data = {"username": "nonexistent@example.com", "password": "wrongpassword"}
    response = await client.post("/auth/token", data=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

# Teste de login com credenciais inválidas para administrador
@pytest.mark.asyncio
async def test_admin_login_invalid_credentials(client: AsyncClient):
    login_data = {"username": "nonexistent_admin", "password": "wrongpassword"}
    response = await client.post("/auth/admin/token", data=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

# Teste de login de usuário com senha incorreta
@pytest.mark.asyncio
async def test_user_login_incorrect_password(client: AsyncClient, db_session_override: Session):
    user_password = "UserSenha1234!"
    await create_test_user(db_session_override, "User Pass Test", "user.pass@example.com", user_password)

    login_data = {"username": "user.pass@example.com", "password": "wrong_password"}
    response = await client.post("/auth/token", data=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

# Teste de login de administrador com senha incorreta
@pytest.mark.asyncio
async def test_admin_login_incorrect_password(client: AsyncClient, db_session_override: Session):
    admin_password = "AdminSnh123!"
    await create_test_admin_user(db_session_override, "Admin Pass Test", admin_password)

    login_data = {"username": "Admin Pass Test", "password": "wrong_password"}
    response = await client.post("/auth/admin/token", data=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

# Teste de acesso a rota protegida sem token
@pytest.mark.asyncio
async def test_protected_route_no_token(client: AsyncClient):
    response = await client.get("/users/me") # Exemplo de rota protegida
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# Teste de acesso a rota protegida com token inválido
@pytest.mark.asyncio
async def test_protected_route_invalid_token(client: AsyncClient):
    headers = {"Authorization": "Bearer invalid_token"}
    response = await client.get("/users/me", headers=headers) # Exemplo de rota protegida
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"