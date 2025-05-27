# File: backend/tests/conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from src.db.database import Base, get_db
# Removidos os imports de schemas UserCreate e AdminUserCreate, pois não serão usados diretamente no construtor
# from src.schemas.user import UserCreate
# from src.schemas.admin_user import AdminUserCreate
from src.models.user import User
from src.models.admin_user import AdminUser
from src.models.employee import Employee
from src.models.briefing import Briefing
from src.models.conversation_history import ConversationHistory
from src.core.security import get_password_hash # Para hash de senhas
from src.core.config import settings
from src.utils.datetime_utils import get_current_datetime_str # Para timestamps

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
        # Limpa o admin padrão, se houver um criado por um evento de startup desabilitado.
        session.query(AdminUser).filter(AdminUser.username == settings.DEFAULT_ADMIN_USERNAME).delete()
        # Se 'User' também puder ser o default_admin_username, você pode querer limpar aqui também.
        session.query(User).filter(User.email == settings.DEFAULT_ADMIN_USERNAME).delete()
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
    hashed_password_value = get_password_hash(password) # Renomeado para evitar conflito com 'hashed_password' de antes
    
    new_user = User(
        name=name,
        email=email,
        # 'phone_number', 'google_id', 'github_id', 'two_factor_secret' podem ser None por padrão
        # 'status' tem default='active' no modelo
    )
    
    # ATRIBUIR AO ATRIBUTO CORRETO: password_hash
    new_user.password_hash = hashed_password_value
    
    # Atribuir outros campos se eles não tiverem defaults adequados ou precisarem ser específicos para o teste
    # No seu modelo User:
    # email_verified = Column(Boolean, default=False) -> OK, não precisa setar
    # creation_date = Column(String(19), nullable=False) -> precisa ser setado ou ter default
    # last_login = Column(String(19), nullable=True) -> pode ser None ou setado
    
    new_user.creation_date = get_current_datetime_str()
    # Se 'last_login' pode ser NULL e você não quer setar agora: new_user.last_login = None
    # Se você quer setar explicitamente:
    new_user.last_login = get_current_datetime_str()
    
    # Remover qualquer atribuição a 'is_admin' se esta coluna NÃO EXISTE no modelo User.
    # Baseado no seu user.py, 'is_admin' NÃO É uma coluna em User.
    # Então, NUNCA FAÇA: new_user.is_admin = False
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def create_test_admin_user(db: Session, username: str, password: str) -> AdminUser:
    """Cria um usuário administrador de teste no banco de dados."""
    hashed_password_value = get_password_hash(password) # Renomeado
    
    new_admin_user = AdminUser(
        username=username,
        # 'two_factor_secret', 'is_two_factor_enabled' têm defaults ou podem ser None
    )
    
    # ATRIBUIR AO ATRIBUTO CORRETO: password_hash
    new_admin_user.password_hash = hashed_password_value
    
    # Atribuir outros campos se eles não tiverem defaults adequados ou precisarem ser específicos para o teste
    # No seu modelo AdminUser:
    # is_two_factor_enabled = Column(Boolean, default=False) -> OK
    # creation_date = Column(String(19), nullable=False) -> precisa ser setado ou ter default
    # last_login = Column(String(19), nullable=True) -> pode ser None ou setado
    
    new_admin_user.creation_date = get_current_datetime_str()
    new_admin_user.last_login = get_current_datetime_str()

    db.add(new_admin_user)
    db.commit()
    db.refresh(new_admin_user)
    return new_admin_user

def get_user_token(client: TestClient, db: Session, email: str, password: str) -> str:
    """Realiza o login de um usuário comum e retorna o token de acesso."""
    login_data = {"username": email, "password": password}
    response = client.post("/auth/login", data=login_data) # CORRIGIDO: Rota /auth/login
    response.raise_for_status()
    return response.json()["access_token"]

def get_admin_token(client: TestClient, db: Session, username: str, password: str) -> str:
    """Realiza o login de um admin e retorna o token de acesso."""
    login_data = {"username": username, "password": password}
    response = client.post("/auth/login", data=login_data) # CORRIGIDO: Rota /auth/login
    response.raise_for_status()
    return response.json()["access_token"]