# src/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import time
from src.core.config import settings

DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL:
    raise ValueError(
        "A variável DATABASE_URL não foi definida nas configurações da aplicação."
    )

MAX_RETRIES = 10
RETRY_DELAY_SECONDS = 5
engine = None

for i in range(MAX_RETRIES):
    try:
        print(f"Tentando conectar ao banco de dados... Tentativa {i + 1}/{MAX_RETRIES}")
        temp_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with temp_engine.connect() as connection:
            connection.close()
        
        engine = temp_engine 
        print("Conexão bem-sucedida com o banco de dados!")
        break
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        if i < MAX_RETRIES - 1:
            print(f"Aguardando {RETRY_DELAY_SECONDS} segundos para tentar novamente...")
            time.sleep(RETRY_DELAY_SECONDS)
        else:
            raise ConnectionError(f"Falha ao conectar ao banco de dados após {MAX_RETRIES} tentativas: {e}")

if engine is None:
    raise ConnectionError("Falha crítica: O motor do banco de dados não foi inicializado após múltiplas tentativas.")

Base = declarative_base() 

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()