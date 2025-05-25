# src/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import time
# >>> CORREÇÃO: Importar 'settings' do nosso módulo de configuração <<<
from src.core.config import settings

# >>> CORREÇÃO: Obter DATABASE_URL diretamente de 'settings' <<<
# 'settings' já leu DATABASE_URL do docker-compose.yml
DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL:
    # Esta verificação é mais uma segurança, pois 'settings' deve garantir que ela exista
    raise ValueError(
        "A variável DATABASE_URL não foi definida nas configurações da aplicação."
    )

# >>> Lógica de Retry para Conexão com o Banco de Dados (Mantida) <<<
MAX_RETRIES = 10
RETRY_DELAY_SECONDS = 5
engine = None # Inicializa engine como None antes do loop de tentativas

for i in range(MAX_RETRIES):
    try:
        print(f"Tentando conectar ao banco de dados... Tentativa {i + 1}/{MAX_RETRIES}")
        # Tenta criar o engine e fazer uma conexão de teste
        # Usando pool_pre_ping=True como você já tinha, o que é bom.
        temp_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with temp_engine.connect() as connection:
            connection.close() # Fecha a conexão de teste imediatamente
        
        # Se a conexão de teste for bem-sucedida, atribui ao engine global e sai do loop
        engine = temp_engine 
        print("Conexão bem-sucedida com o banco de dados!")
        break # Sai do loop porque a conexão foi estabelecida
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        if i < MAX_RETRIES - 1: # Verifica se ainda há tentativas restantes
            print(f"Aguardando {RETRY_DELAY_SECONDS} segundos para tentar novamente...")
            time.sleep(RETRY_DELAY_SECONDS)
        else:
            # Se todas as tentativas falharem, levanta a exceção
            raise ConnectionError(f"Falha ao conectar ao banco de dados após {MAX_RETRIES} tentativas: {e}")

# Garante que o 'engine' foi inicializado.
if engine is None:
    raise ConnectionError("Falha crítica: O motor do banco de dados não foi inicializado após múltiplas tentativas.")
# <<< FIM DA LÓGICA DE RETRY PARA CONEXÃO COM O BANCO DE DADOS >>>


# Base definida para os modelos do SQLAlchemy
Base = declarative_base()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependência para criar a sessão (esta função está perfeita aqui)
def get_db():
    """
    Retorna uma sessão de banco de dados para ser usada nas requisições.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()