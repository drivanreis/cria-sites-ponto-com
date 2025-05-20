# src/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from decouple import config

# Obtém a URL do banco de dados diretamente do .env
DATABASE_URL = config("DATABASE_URL", default=None)
if not DATABASE_URL:
    raise ValueError(
        "A variável DATABASE_URL não foi definida no arquivo .env."
    )


try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as connection:
        print("Conexão bem-sucedida com o banco de dados!")
except Exception as e:
    raise ConnectionError(f"Erro ao conectar ao banco de dados: {e}")

# Base definida para os modelos do SQLAlchemy
Base = declarative_base()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependência para criar a sessão
def get_db():
    """
    Retorna uma sessão de banco de dados para ser usada nas requisições.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()