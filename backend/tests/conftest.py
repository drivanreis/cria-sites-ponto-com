# File: backend/tests/conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from src.db.database import Base, get_db
from src.models.user import User
from src.models.admin_user import AdminUser
from src.models.employee import Employee
from src.models.briefing import Briefing
from src.models.conversation_history import ConversationHistory
from src.core.security import get_password_hash
from src.core.config import settings
from src.utils.datetime_utils import get_current_datetime_str

# Configuração do banco de dados de teste
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session_override():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        session.query(AdminUser).filter(AdminUser.username == settings.DEFAULT_ADMIN_USERNAME).delete()
        session.query(User).filter(User.email == settings.DEFAULT_ADMIN_USERNAME).delete() # Se DEFAULT_ADMIN_USERNAME pode ser um email de usuário
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Warning: Could not clear default admin from test DB: {e}")

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session_override: Session):
    from src.main import app

    app.dependency_overrides[get_db] = lambda: db_session_override

    original_startup_events = list(app.router.on_startup)
    app.router.on_startup = []

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    app.router.on_startup = original_startup_events


# --- Funções Auxiliares para Testes ---

def create_test_user(db: Session, name: str, email: str, password: str) -> User:
    """Cria um usuário comum de teste no banco de dados."""
    hashed_password_value = get_password_hash(password)
    current_datetime_str = get_current_datetime_str() # Obter uma vez para consistência
    
    # Criar um dicionário com os dados que correspondem exatamente às COLUNAS do modelo User
    user_data = {
        "name": name,
        "email": email,
        "password_hash": hashed_password_value, # CORRIGIDO: Usando 'password_hash'
        "creation_date": current_datetime_str,
        "last_login": current_datetime_str,
        "email_verified": False,
        "status": "active", # Conforme o default do seu modelo User
        # 'phone_number', 'google_id', 'github_id', 'two_factor_secret', 'is_two_factor_enabled'
        # são nullable=True ou têm defaults no modelo, então não precisam ser passados
        # a menos que você queira um valor específico para o teste.
    }
    
    new_user = User(**user_data) # Instanciar o modelo a partir do dicionário
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def create_test_admin_user(db: Session, username: str, password: str) -> AdminUser:
    """Cria um usuário administrador de teste no banco de dados."""
    hashed_password_value = get_password_hash(password)
    current_datetime_str = get_current_datetime_str()
    
    # Criar um dicionário com os dados que correspondem exatamente às COLUNAS do modelo AdminUser
    admin_user_data = {
        "username": username,
        "password_hash": hashed_password_value, # CORRIGIDO: Usando 'password_hash'
        "creation_date": current_datetime_str,
        "last_login": current_datetime_str,
        "is_two_factor_enabled": False, # Conforme o default do seu modelo AdminUser
        # 'two_factor_secret' é nullable=True, então não precisa ser passado
    }
    
    new_admin_user = AdminUser(**admin_user_data) # Instanciar o modelo a partir do dicionário
    
    db.add(new_admin_user)
    db.commit()
    db.refresh(new_admin_user)
    return new_admin_user

def get_user_token(client: TestClient, db: Session, email: str, password: str) -> str:
    """Realiza o login de um usuário comum e retorna o token de acesso."""
    login_data = {"username": email, "password": password}
    response = client.post("/auth/login", data=login_data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_admin_token(client: TestClient, db: Session, username: str, password: str) -> str:
    """Realiza o login de um admin e retorna o token de acesso."""
    login_data = {"username": username, "password": password}
    response = client.post("/auth/login", data=login_data)
    response.raise_for_status()
    return response.json()["access_token"]