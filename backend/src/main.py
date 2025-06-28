# File: backend/src/main.py (após as modificações)

from fastapi import FastAPI, Depends, HTTPException, status
import uvicorn
import os
import sys
from src.db.database import get_db, Session
import time
from src.utils.datetime_utils import get_current_datetime_str

from src.middlewares.cors import CORS_MIDDLEWARE_SETTINGS
from fastapi.middleware.cors import CORSMiddleware

from src.routers import admin_user_routers, briefing_routers, \
                            employee_routers, user_routers, \
                            auth_admin_routers, auth_user_routers, auth_social_routers

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.abspath(os.path.join(current_dir, "../"))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from src.db.database import SessionLocal, engine, Base
import src.models # <--- Mantenha esta importação para o SQLAlchemy conhecer seus modelos

app = FastAPI(
    title="Cria Sites .com API",
    description="API para gerenciamento de usuários, briefings e histórico de conversas.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_MIDDLEWARE_SETTINGS["allow_origins"],
    allow_credentials=CORS_MIDDLEWARE_SETTINGS["allow_credentials"],
    allow_methods=CORS_MIDDLEWARE_SETTINGS["allow_methods"],
    allow_headers=CORS_MIDDLEWARE_SETTINGS["allow_headers"],
)

@app.on_event("startup")
async def startup_event_handler():
    print("Iniciando a lógica de startup da aplicação...")

    MAX_RETRIES = 5
    RETRY_DELAY_SECONDS = 5

    for i in range(MAX_RETRIES):
        try:
            print(f"Tentando conectar ao banco de dados (tentativa {i + 1}/{MAX_RETRIES})...")
            with engine.connect() as connection:
                pass # Apenas testa a conexão
            print("Conexão com o banco de dados estabelecida com sucesso.")
            break
        except Exception as e:
            print(f"Falha ao conectar ao banco de dados: {e}")
            if i < MAX_RETRIES - 1:
                print(f"Aguardando {RETRY_DELAY_SECONDS} segundos antes de tentar novamente...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                print("Número máximo de tentativas de conexão atingido. Exiting.")
                sys.exit(1)
    
    print("Lógica de startup da aplicação concluída.")

app.include_router(user_routers.router)
app.include_router(admin_user_routers.router)
app.include_router(employee_routers.router)
app.include_router(briefing_routers.router)
app.include_router(auth_admin_routers.router)
app.include_router(auth_user_routers.router)
app.include_router(auth_social_routers.router)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Backend!"
    " minha hora local é " + get_current_datetime_str()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# /home/eu/.config/ngrok/ngrok.yml