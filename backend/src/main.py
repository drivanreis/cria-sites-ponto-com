# File: backend/src/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uvicorn
import os
import sys

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
from src.routers import user, admin_user, employee, briefing, conversation_history

# Cria as tabelas no banco de dados, se ainda não existirem.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cria Sites .com API",
    description="API para gerenciamento de usuários, briefings e histórico de conversas.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# >>> Adição do Middleware CORS
app.add_middleware(
    CORSMiddleware,
    **CORS_MIDDLEWARE_SETTINGS
)
# <<< Fim da adição do Middleware CORS

# Dependency para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Incluir os routers
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(admin_user.router, prefix="/admin_users", tags=["admin_users"])
app.include_router(employee.router, prefix="/employees", tags=["employees"])
app.include_router(briefing.router, prefix="/briefings", tags=["briefings"])
app.include_router(conversation_history.router, prefix="/conversation_history", tags=["conversation_history"])


@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API Cria Sites .com!"}

# Para rodar o aplicativo diretamente (opcional, docker-compose fará isso)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)