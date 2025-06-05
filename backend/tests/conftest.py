# File: backend/tests/conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, configure_mappers # Importado configure_mappers
from fastapi.testclient import TestClient
from src.db.database import Base, get_db
from src.models.user_models import User
from src.models.admin_user_models import AdminUser
from src.models.employee_models import Employee
from src.models.briefing_models import Briefing
from src.models.conversation_history_models import ConversationHistory
from src.core.security import get_password_hash
from src.core.config import settings
from src.utils.datetime_utils import get_current_datetime_str

# Importar a aplicação FastAPI para o cliente de teste
from src.main import app # Importado para o topo para consistência

# Configuração do banco de dados de teste
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Cria as tabelas do banco de dados antes de todos os testes da sessão
    e as remove após a conclusão de todos os testes.
    """
    # Garante que todos os modelos são importados e conhecidos pela Base.metadata.
    # As importações no topo do arquivo já fazem isso, executando os módulos de modelo.

    # Explicitamente configura os mappers antes de criar as tabelas.
    # Isso é crucial para garantir que todos os relacionamentos sejam registrados
    # antes que o SQLAlchemy tente criar as tabelas ou fazer queries.
    configure_mappers() # Chamada adicionada aqui!
    
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session_override():
    """
    Fornece uma sessão de banco de dados por teste,
    garantindo que cada teste comece com um estado limpo.
    Os dados são revertidos ao final de cada teste.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # --- LIMPEZA DE DADOS (ORDEM DE DEPENDÊNCIA É CRÍTICA!) ---
    # Deletar os filhos antes dos pais para evitar violações de chave estrangeira
    session.query(ConversationHistory).delete() # Depende de Briefing
    session.query(Briefing).delete()            # Depende de User
    session.query(Employee).delete()            # Independente
    session.query(User).delete()                # Pais
    session.query(AdminUser).delete()           # Pais
    session.commit() # Commit as deleções para que o estado do DB esteja limpo antes do teste

    yield session

    session.close()
    transaction.rollback() # Reverte todas as operações do teste, garantindo limpeza
    connection.close()

@pytest.fixture(scope="function")
def client(db_session_override: Session):
    """
    Cria um cliente de teste para a aplicação FastAPI.
    Sobrescreve a dependência do DB e lida com eventos de startup/shutdown.
    """
    app.dependency_overrides[get_db] = lambda: db_session_override

    # Desativa eventos de startup para testes, pois eles podem tentar inicializar DB, etc.
    original_startup_events = list(app.router.on_startup)
    app.router.on_startup = []

    with TestClient(app) as test_client:
        yield test_client

    # Limpa as sobrescrições e restaura os eventos de startup após o teste
    app.dependency_overrides.clear()
    app.router.on_startup = original_startup_events


# --- Funções Auxiliares para Testes ---

def create_test_user(db: Session, name: str, email: str, password: str) -> User:
    """Cria um usuário comum de teste no banco de dados."""
    hashed_password_value = get_password_hash(password)
    current_datetime = get_current_datetime_str() # Obter uma vez para consistência
    
    new_user = User(
        name=name,
        email=email,
        password_hash=hashed_password_value,
        creation_date=current_datetime,
        last_login=current_datetime,
        email_verified=False,
        status="active",
        phone_number="11999999999" # Adicionado para garantir que o campo não-nullable seja preenchido, se for o caso
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def create_test_admin_user(db: Session, username: str, password: str) -> AdminUser:
    """Cria um usuário administrador de teste no banco de dados."""
    hashed_password_value = get_password_hash(password)
    current_datetime = get_current_datetime_str()
    
    new_admin_user = AdminUser(
        username=username,
        password_hash=hashed_password_value,
        creation_date=current_datetime,
        last_login=current_datetime,
        is_two_factor_enabled=False,
    )
    
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

# --- NOVA FUNÇÃO AUXILIAR PARA EMPLOYEES ---
def create_test_employee(db: Session, employee_name: str, ia_name: str = "TestIA", endpoint_url: str = "http://test.com", endpoint_key: str = "key", employee_script: dict = None, headers_template: dict = None, body_template: dict = None):
    """Cria um registro de Employee de teste e o adiciona ao banco de dados."""
    if employee_script is None:
        employee_script = {"purpose": "testing"}
    if headers_template is None:
        headers_template = {"X-Test-Header": "value"}
    if body_template is None:
        body_template = {"test_body_param": "value"}

    current_datetime = get_current_datetime_str()

    new_employee = Employee(
        employee_name=employee_name,
        employee_script=employee_script,
        ia_name=ia_name,
        endpoint_url=endpoint_url,
        endpoint_key=endpoint_key,
        headers_template=headers_template,
        body_template=body_template,
        last_update=current_datetime
    )
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee