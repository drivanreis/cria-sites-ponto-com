# alembic/env.py

import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from decouple import config as decouple_config

# Adiciona o diretório raiz ao sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

# Configura o logger a partir do arquivo de configuração do Alembic
if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)

# Carrega a URL do banco de dados a partir do .env
database_url = decouple_config("DATABASE_URL", default=None)
if not database_url:
    raise RuntimeError(
        "DATABASE_URL não está configurado no .env ou não foi encontrado."
    )
config = context.config
config.set_main_option("sqlalchemy.url", database_url)

# Importa as models e configura o target_metadata
from src.db.database import Base

# Importação explícita das models, garantindo ordem
from src.models.admin_user_models import AdminUser
from src.models.employee_models import Employee
from src.models.user_models import User
from src.models.briefing_models import Briefing
from src.models.conversation_history_models import ConversationHistory



# Definindo o target_metadata para o Alembic
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Executa as migrações no modo offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa as migrações no modo online."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Verifica tipos de colunas
        )
        with context.begin_transaction():
            context.run_migrations()


# Executa as migrações com base no modo (online ou offline)
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()