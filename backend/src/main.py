# File: backend/src/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uvicorn
import os
import sys
# >>> NOVIDADE: Adicionar import de time para o retry no DB (próximo passo) <<<
import time

# >>> Adição para CORS
from fastapi.middleware.cors import CORSMiddleware
from src.middlewares.cors import CORS_MIDDLEWARE_SETTINGS
# <<< Fim da adição para CORS

# Adiciona o diretório raiz do backend ao sys.path
# Isso é crucial para que `src.db`, `src.routers` e outros módulos sejam encontrados.
# Assume que este arquivo está em backend/src/
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.abspath(os.path.join(current_dir, "../"))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

# Importações após ajustar sys.path
from src.db.database import SessionLocal, engine, Base
from src.routers import user, admin_user, employee, briefing, conversation_history, auth
from src.cruds import admin_user as crud_admin_user
from src.schemas.admin_user import AdminUserCreate
from src.schemas.user import UserCreate
from src.core.config import settings

# >>> CORREÇÃO: Criar a instância 'app' AQUI, antes de qualquer uso dela <<<
app = FastAPI(
    title="Cria Sites .com API",
    description="API para gerenciamento de usuários, briefings e histórico de conversas.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Adiciona o middleware CORS
app.add_middleware(
    CORSMiddleware,
    **CORS_MIDDLEWARE_SETTINGS
)

# O evento de startup deve vir DEPOIS que 'app' é definido
@app.on_event("startup")
def create_default_admin_user_on_startup():
    db = SessionLocal()
    try:
        # Verifica se o admin padrão já existe
        # Use o username do admin para a consulta
        existing_admin = crud_admin_user.get_admin_user_by_username(db, settings.DEFAULT_ADMIN_USERNAME)

        if not existing_admin:
            if settings.DEFAULT_ADMIN_USERNAME and settings.DEFAULT_ADMIN_PASSWORD:
                # Use SOMENTE os campos definidos em AdminUserCreate
                admin_create = AdminUserCreate(
                    username=settings.DEFAULT_ADMIN_USERNAME,
                    password=settings.DEFAULT_ADMIN_PASSWORD,
                    # REMOVIDOS: email e full_name, pois AdminUserCreate não os define
                )
                crud_admin_user.create_admin_user(db=db, admin_user=admin_create)
                print(f"Usuário admin '{settings.DEFAULT_ADMIN_USERNAME}' criado com sucesso!")
            else:
                print("DEFAULT_ADMIN_USERNAME ou DEFAULT_ADMIN_PASSWORD não configurados. Não foi possível criar admin padrão.")
        else:
            print(f"Usuário admin '{settings.DEFAULT_ADMIN_USERNAME}' já existe. Nenhuma ação necessária.")
    except Exception as e:
        print(f"Erro ao verificar/criar usuário admin padrão: {e}")
    finally:
        db.close()

# Cria as tabelas no banco de dados, se ainda não existirem.
# Base.metadata.create_all(bind=engine) # Mantido comentado


# Dependency para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Incluir os routers
app.include_router(user.router)
app.include_router(admin_user.router)
app.include_router(employee.router)
app.include_router(briefing.router)
app.include_router(conversation_history.router)
app.include_router(auth.router)


@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API Cria Sites .com!"}

# Para rodar o aplicativo diretamente (opcional, docker-compose fará isso)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)