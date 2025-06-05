# File: backend/src/main.py

from fastapi import FastAPI, Depends, HTTPException, status
import uvicorn
import os
import sys
from src.db.database import get_db, Session
import time # Importado para o retry no DB

# >>> Correção CORS: Importando diretamente de src.middlewares.cors
from src.middlewares.cors import CORS_MIDDLEWARE_SETTINGS
from fastapi.middleware.cors import CORSMiddleware # CORSMiddleware é da FastAPI, não do nosso arquivo CORS
# <<< Fim da correção CORS

# --- Importações de Routers (ajustadas conforme sua versão mais recente) ---
from src.routers import admin_user_routers, auth_routers, briefing_routers, \
                        employee_routers, user_routers

# Adiciona o diretório raiz do backend ao sys.path
# Isso é crucial para que `src.db`, `src.routers` e outros módulos sejam encontrados.
# Assume que este arquivo está em backend/src/
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.abspath(os.path.join(current_dir, "../"))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

# Importações após ajustar sys.path
from src.db.database import SessionLocal, engine, Base
# Importações necessárias para os testes
from src.models import user_models, admin_user_models, employee_models, \
                       briefing_models, conversation_history_models
from src.cruds import admin_user_cruds
from src.cruds import employee_cruds # Importar o crud de employees
from src.schemas.admin_user_schemas import AdminUserCreate
from src.schemas.employee_schemas import EmployeeCreateInternal # Importar schema para Employees
from src.schemas.user_schemas import UserCreate # Manter se necessário
from src.core.config import settings
from src.utils.employees_data import REQUIRED_EMPLOYEES_DATA # Importar os dados dos employees

# Cria a instância 'app' AQUI, antes de qualquer uso dela
app = FastAPI(
    title="Cria Sites .com API",
    description="API para gerenciamento de usuários, briefings e histórico de conversas.",
    version="0.1.0"
)

# Adicionar middleware CORS (AGORA USANDO SUAS DEFINIÇÕES CORRETAMENTE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_MIDDLEWARE_SETTINGS["allow_origins"],
    allow_credentials=CORS_MIDDLEWARE_SETTINGS["allow_credentials"],
    allow_methods=CORS_MIDDLEWARE_SETTINGS["allow_methods"],
    allow_headers=CORS_MIDDLEWARE_SETTINGS["allow_headers"],
)


# --- Lógica de Inicialização da Aplicação (Startup Event) ---
# Esta função será executada quando o FastAPI iniciar.
@app.on_event("startup")
async def startup_event_handler():
    print("Iniciando a lógica de startup da aplicação...")

    # Tentar conectar ao banco de dados e criar tabelas com retries
    MAX_RETRIES = 5
    RETRY_DELAY_SECONDS = 5

    for i in range(MAX_RETRIES):
        try:
            print(f"Tentando conectar ao banco de dados e criar tabelas (tentativa {i + 1}/{MAX_RETRIES})...")
            # Cria as tabelas no banco de dados, se ainda não existirem.
            with engine.connect() as connection: # Usar engine.connect() para garantir a conexão
                Base.metadata.create_all(bind=connection)
            print("Tabelas do banco de dados verificadas/criadas com sucesso.")
            break # Sai do loop se a conexão e criação forem bem-sucedidas
        except Exception as e:
            print(f"Falha ao conectar ao banco de dados ou criar tabelas: {e}")
            if i < MAX_RETRIES - 1:
                print(f"Aguardando {RETRY_DELAY_SECONDS} segundos antes de tentar novamente...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                print("Número máximo de tentativas de conexão/criação de tabelas atingido. Exiting.")
                sys.exit(1) # Sai da aplicação se não conseguir conectar ao DB

    # Lógica para criar o usuário admin padrão
    db: Session = next(get_db()) # Obtém uma sessão do banco de dados
    try:
        existing_admin = admin_user_cruds.get_admin_user_by_username(db, settings.DEFAULT_ADMIN_USERNAME)
        if not existing_admin:
            if settings.DEFAULT_ADMIN_USERNAME and settings.DEFAULT_ADMIN_PASSWORD:
                admin_create = AdminUserCreate(
                    username=settings.DEFAULT_ADMIN_USERNAME,
                    password=settings.DEFAULT_ADMIN_PASSWORD,
                )
                admin_user_cruds.create_admin_user(db=db, admin_user=admin_create)
                print(f"Usuário admin '{settings.DEFAULT_ADMIN_USERNAME}' criado com sucesso!")
            else:
                print("DEFAULT_ADMIN_USERNAME ou DEFAULT_ADMIN_PASSWORD não configurados. Não foi possível criar admin padrão.")
        else:
            print(f"Usuário admin '{settings.DEFAULT_ADMIN_USERNAME}' já existe. Nenhuma ação necessária.")
    except Exception as e:
        print(f"Erro ao verificar/criar usuário admin padrão: {e}")
    finally:
        db.close()

    # Lógica para criar os Employees (personagens) padrão
    db_employee_session: Session = next(get_db()) # Nova sessão para employees
    try:
        print("Verificando e criando Employees (personagens) padrão...")
        for emp_data_raw in REQUIRED_EMPLOYEES_DATA:
            validated_data = EmployeeCreateInternal(**emp_data_raw)
            existing_employee = employee_cruds.get_employee_by_name(db_employee_session, sender_type=validated_data.sender_type)
            
            if not existing_employee:
                print(f"Criando registro de funcionário mínimo: {validated_data.sender_type}")
                employee_cruds.create_employee_initial(db_employee_session, validated_data)
            else:
                print(f"Registro de funcionário mínimo já existe: {validated_data.sender_type}")
    except Exception as e:
        print(f"Erro ao verificar/criar Employees padrão: {e}")
    finally:
        db_employee_session.close()
    
    print("Lógica de startup da aplicação concluída.")


# Incluir os routers
app.include_router(user_routers.router)
app.include_router(admin_user_routers.router)
app.include_router(employee_routers.router)
app.include_router(briefing_routers.router)
app.include_router(auth_routers.router)


@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API Cria Sites .com!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)