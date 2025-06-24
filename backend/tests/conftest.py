import pytest
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, configure_mappers
from fastapi.testclient import TestClient
from typing import Optional

# --- Importações da Aplicação ---
from src.main import app
from src.db.database import Base, get_db
from src.core.security import get_password_hash
from src.core.config import settings
from src.utils.datetime_utils import get_current_datetime_str

# --- Importações de Modelos para Mapeamento e Limpeza ---
# É crucial importar TODOS os modelos aqui para que SQLAlchemy os descubra
# e configure seus mapeamentos e relacionamentos corretamente antes de qualquer operação de DB.
# Ao importar 'src.models', o __init__.py dentro dele garante que todos os modelos são carregados.
import src.models # <--- MUDANÇA PRINCIPAL AQUI: Importa o pacote src.models

# As importações individuais abaixo NÃO SÃO MAIS NECESSÁRIAS AQUI,
# pois src.models já as carrega via src/models/__init__.py.
# Deixo-as comentadas para referência, mas podem ser removidas.
# from src.models.user_models import User
# from src.models.admin_user_models import AdminUser
# from src.models.employee_models import Employee
# from src.models.briefing_models import Briefing
# from src.models.conversation_history_models import ConversationHistory

# --- Importações de Schemas e CRUDS para Funções Auxiliares ---
# Estas continuam sendo necessárias para o uso direto das classes/funções
from src.schemas.user_schemas import UserCreate
from src.schemas.admin_user_schemas import AdminUserCreate
from src.schemas.employee_schemas import EmployeeCreateInternal
from src.cruds import user_cruds
from src.cruds import admin_user_cruds
from src.cruds import employee_cruds

# --- Configuração de Logging para Testes ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuração do Banco de Dados de Teste ---
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Fixture para Setup e Teardown do Banco de Dados da Sessão ---
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Fixture de sessão que configura o banco de dados de teste (cria tabelas)
    antes de todos os testes e limpa (dropa tabelas) após todos os testes.
    A chamada a configure_mappers() é essencial para que o SQLAlchemy
    reconheça todos os relacionamentos antes de criar as tabelas.
    """
    logger.info("Iniciando setup do banco de dados de teste para a sessão.")
    
    # Força o SQLAlchemy a configurar todos os mapeadores.
    # Isso é vital para que os relacionamentos (como conversation_histories em Briefing)
    # sejam reconhecidos antes de qualquer interação com a metadata ou queries.
    configure_mappers()
    
    Base.metadata.create_all(bind=engine) # Cria todas as tabelas definidas nos modelos
    logger.info("Tabelas do banco de dados de teste criadas.")
    yield # Executa os testes
    Base.metadata.drop_all(bind=engine) # Dropa todas as tabelas após os testes
    logger.info("Tabelas do banco de dados de teste removidas.")

# --- Fixture para Sessão do Banco de Dados por Função (Teste) ---
@pytest.fixture(scope="function")
def db_session_override():
    """
    Fixture por função que fornece uma sessão de banco de dados isolada para cada teste.
    Cada teste começa com um banco de dados limpo e os dados são revertidos (rollback)
    ao final do teste para garantir o isolamento.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    logger.info("Iniciando limpeza de dados para um novo teste...")
    # --- LIMPEZA DE DADOS (ORDEM DE DEPENDÊNCIA CRÍTICA PARA FKs) ---
    # Deletar os filhos antes dos pais para evitar violações de chave estrangeira.
    # Agora você pode referenciar os modelos diretamente usando 'src.models.NomeDoModelo'
    session.query(src.models.ConversationHistory).delete() # <--- MUDANÇA AQUI
    session.query(src.models.Briefing).delete()            # <--- MUDANÇA AQUI
    session.query(src.models.Employee).delete()            # <--- MUDANÇA AQUI
    session.query(src.models.User).delete()                # <--- MUDANÇA AQUI
    session.query(src.models.AdminUser).delete()           # <--- MUDANÇA AQUI
    session.commit() # Commit as deleções para que o estado do DB esteja limpo antes do teste iniciar
    logger.info("Dados de teste anteriores limpos.")

    yield session # A sessão é passada para o teste

    session.close() # Fecha a sessão (já feito pelo rollback e close da conexão)
    # ATENÇÃO: Se transaction.rollback() for chamado após session.close(),
    # pode ocorrer um SAWarning: "transaction already deassociated from connection".
    # A ordem correta é: rollback, close session, close connection.
    transaction.rollback() # Reverte todas as operações feitas durante o teste
    connection.close() # Fecha a conexão com o banco de dados
    logger.info("Sessão do banco de dados fechada e transação revertida.")

# --- Fixture para Cliente de Teste FastAPI ---
@pytest.fixture(scope="function")
def client(db_session_override: Session):
    """
    Fixture que fornece um cliente de teste para a aplicação FastAPI.
    Ele sobrescreve a dependência de banco de dados da aplicação para usar
    a sessão de teste isolada e desativa os eventos de startup da aplicação
    para evitar inicializações duplicadas ou indesejadas durante os testes.
    """
    logger.info("Configurando cliente de teste FastAPI.")
    # Sobrescreve a dependência get_db da aplicação para usar a sessão de teste
    app.dependency_overrides[get_db] = lambda: db_session_override

    # Desativa eventos de startup do FastAPI para evitar que eles rodem durante os testes
    original_startup_events = list(app.router.on_startup)
    app.router.on_startup = []

    with TestClient(app) as test_client:
        yield test_client # O cliente de teste é passado para a função de teste

    # Limpa as sobrescrições e restaura os eventos de startup originais após o teste
    app.dependency_overrides.clear()
    app.router.on_startup = original_startup_events
    logger.info("Cliente de teste FastAPI e dependências restauradas.")

# --- Funções Auxiliares para Criação de Entidades de Teste ---
# Essas funções criam e persistem entidades diretamente no DB de teste.

# CORREÇÃO CRÍTICA AQUI: Adicionar phone_number como Optional e passá-lo para UserCreate
def create_test_user(db: Session, nickname: str, email: Optional[str] = None, password: str = "SecureP@ss1", phone_number: Optional[str] = None) -> src.models.User: # <--- MUDANÇA AQUI
    """Cria e persiste um usuário comum de teste no banco de dados.
    Requer pelo menos email OU phone_number, e uma senha forte.
    """
    if email is None and phone_number is None:
        raise ValueError("Pelo menos um email ou um número de telefone deve ser fornecido para o cadastro.")

    if email:
        logger.info(f"Criando usuário de teste com email: {email}")
    elif phone_number:
        logger.info(f"Criando usuário de teste com telefone: {phone_number}")

    # Use UserCreate schema para garantir que os dados de entrada são válidos
    user_schema = UserCreate(
        nickname=nickname,
        email=email,
        phone_number=phone_number,
        password=password # A senha será hashed dentro do user_cruds.create_user
    )
    
    # Chama a função CRUD real para criar o usuário
    new_user = user_cruds.create_user(db, user_schema)
    return new_user

def create_test_admin_user(db: Session, username: str, password: str = "AdminP@ss1") -> src.models.AdminUser: # <--- MUDANÇA AQUI
    """Cria e persiste um usuário administrador de teste no banco de dados."""
    logger.info(f"Criando admin de teste: {username}")
    hashed_password_value = get_password_hash(password)
    current_datetime = get_current_datetime_str()
    
    # Usando o AdminUser model direto para criar no teste, pois AdminUserCreate é mais para API.
    # Se admin_user_cruds.create_admin_user espera um schema, você adaptaria aqui.
    new_admin_user = src.models.AdminUser( # <--- MUDANÇA AQUI
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

def create_test_employee(db: Session, employee_name: str, ia_name: str = "TestIA", endpoint_url: str = "http://test.com", endpoint_key: str = "key", employee_script: dict = None, headers_template: dict = None, body_template: dict = None) -> src.models.Employee: # <--- MUDANÇA AQUI
    """Cria e persiste um registro de Employee de teste no banco de dados."""
    logger.info(f"Criando employee de teste: {employee_name}")
    if employee_script is None:
        employee_script = {"intro": "Hello!", "context": "You are a test assistant."}
    if headers_template is None:
        headers_template = {"Content-Type": "application/json"}
    if body_template is None:
        body_template = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "{{prompt_content}}"}]}

    employee_data = EmployeeCreateInternal(
        employee_name=employee_name,
        employee_script=employee_script,
        ia_name=ia_name,
        endpoint_url=endpoint_url,
        endpoint_key=endpoint_key,
        headers_template=headers_template,
        body_template=body_template,
    )
    
    # Chama o CRUD real para criar o employee
    new_employee = employee_cruds.create_employee(db, employee_data)
    return new_employee

# --- Funções Auxiliares para Obtenção de Tokens API ---
# Essas funções interagem com o cliente de teste FastAPI para simular logins.

def get_user_token(client: TestClient, db: Session, email: Optional[str] = None, password: Optional[str] = None, phone_number: Optional[str] = None) -> str:
    """Realiza o login de um usuário comum via API e retorna o token de acesso.
    Deve-se fornecer email OU phone_number para o login.
    """
    logger.info(f"Obtendo token para usuário: {email or phone_number}")
    login_data = {}
    if email:
        login_data["username"] = email # FastAPI padrão para username é email
    elif phone_number:
        login_data["username"] = phone_number # Se seu login permite telefone
    else:
        raise ValueError("Deve-se fornecer email ou número de telefone para o login.")
    
    if not password:
        raise ValueError("A senha é obrigatória para o login.")

    login_data["password"] = password

    # Assumindo que seu endpoint de login é /auth/login e não /auth/token
    response = client.post("/auth/login", data=login_data)
    response.raise_for_status() # Levanta exceção para status codes de erro (4xx ou 5xx)
    return response.json()["access_token"]

def get_admin_token(client: TestClient, db: Session, username: str, password: str) -> str:
    """Realiza o login de um admin via API e retorna o token de acesso."""
    logger.info(f"Obtendo token para admin: {username}")
    login_data = {"username": username, "password": password}
    # Assumindo que seu endpoint de login admin é /auth/login (mesmo para user e admin)
    response = client.post("/auth/login", data=login_data) # Alterado de /auth/admin/token para /auth/login
    response.raise_for_status() # Levanta exceção para status codes de erro (4xx ou 5xx)
    return response.json()["access_token"]