# File: backend/tests/conftest.py

import pytest
# import asyncio # Não necessário aqui, o pytest-asyncio já cuida
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# --- Importações absolutas do 'src' ---
from src.main import app
from src.db.database import get_db, Base
from src.core.config import settings

# Importe explicitamente seus modelos aqui para que Base.metadata.create_all() os conheça
from src.models.admin_user import AdminUser
from src.models.user import User

# Importe os schemas e CRUDS necessários para as funções auxiliares
from src.schemas.user import UserCreate
from src.schemas.admin_user import AdminUserCreate
from src.cruds import user as crud_user
from src.cruds import admin_user as crud_admin_user
from src.core.security import create_access_token


# --- Fixture para a sessão do banco de dados de teste ---
@pytest.fixture(scope="function")
def db_session_override():
    test_engine = create_engine(settings.DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # CRUCIAL: Limpa e recria todas as tabelas para cada teste
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        test_engine.dispose()

# --- Fixture para o cliente HTTP de teste (CORREÇÃO FINAL AQUI!) ---
@pytest.fixture(scope="function")
async def client(db_session_override: Session):
    # Sobrescreve a dependência get_db do FastAPI para usar a sessão de teste
    app.dependency_overrides[get_db] = lambda: db_session_override

    # Crie o cliente sem usar 'async with' diretamente na fixture
    _client = AsyncClient(app=app, base_url="http://test")

    # Entre no contexto assíncrono manualmente
    await _client.__aenter__()

    # Ceda o cliente para os testes
    yield _client

    # Saia do contexto assíncrono manualmente, garantindo que seja fechado
    await _client.__aexit__(None, None, None)

    # Limpa a sobrescrita de dependência após o teste
    app.dependency_overrides.clear()


# --- Funções Auxiliares Comuns para Testes ---
async def create_test_user(db: Session, name: str, email: str, password: str):
    user_data = UserCreate(name=name, email=email, password=password)
    test_user = crud_user.create_user(db, user_data)
    return {"id": test_user.id, "name": test_user.name, "email": test_user.email, "password": password}

async def create_test_admin_user(db: Session, username: str, password: str):
    admin_data = AdminUserCreate(username=username, password=password)
    admin = crud_admin_user.create_admin_user(db, admin_data)
    return {"id": admin.id, "username": admin.username, "password": password}

async def get_user_token(client: AsyncClient, db_session: Session, email: str, password: str):
    await create_test_user(db_session, "Auth User For Token", email, password)
    login_data = {"username": email, "password": password}
    response = await client.post("/auth/token", data=login_data)
    assert response.status_code == 200, f"Falha ao obter token de usuário. Status: {response.status_code}, Detalhe: {response.json().get('detail', 'Nenhum detalhe')}"
    token = response.json()["access_token"]
    return {"access_token": token, "token_type": "bearer"}

async def get_admin_token(client: AsyncClient, db_session: Session, username: str, password: str):
    await create_test_admin_user(db_session, username, password)
    login_data = {"username": username, "password": password}
    response = await client.post("/auth/admin/token", data=login_data)
    assert response.status_code == 200, f"Falha ao obter token de admin. Status: {response.status_code}, Detalhe: {response.json().get('detail', 'Nenhum detalhe')}"
    token = response.json()["access_token"]
    return {"access_token": token, "token_type": "bearer"}