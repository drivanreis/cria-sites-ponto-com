# File: backend/src/startup.py (APENAS A PARTE DA FUNÇÃO populate_initial_data)

import os
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Adiciona o diretório raiz do backend ao sys.path para importações relativas
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.abspath(os.path.join(current_dir, "../"))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

# Importações dos modelos e utilitários
from src.db.database import DATABASE_URL
from src.models.admin_user_models import AdminUser
from src.models.employee_models import Employee # Mantenha esta
from src.core.security import get_password_hash
from src.utils.datetime_utils import get_current_datetime_str
from src.core.config import settings
from src.utils.employees_data import REQUIRED_EMPLOYEES_DATA # Mantenha esta

# REMOVA estas importações se elas eram APENAS para a lógica de população de funcionários:
# from src.cruds import employee_cruds # NÃO USAR
# from src.schemas.employee_schemas import EmployeeCreateInternal # NÃO USAR AQUI, usar o dict direto


def populate_initial_data():
    """
    Popula dados iniciais no banco de dados, incluindo o usuário admin e employees.
    Este script deve ser executado APÓS as tabelas serem criadas pelo Alembic.
    """
    print("Iniciando a população de dados iniciais...")

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal() # Use esta sessão para TUDO, admin e employees

    try:
        # --- Popular Usuário Admin Padrão (Manter como está, já está funcionando) ---
        default_admin_username = settings.DEFAULT_ADMIN_USERNAME
        default_admin_password = settings.DEFAULT_ADMIN_PASSWORD

        existing_admin = session.query(AdminUser).filter_by(username=default_admin_username).first()

        if not existing_admin:
            if default_admin_username and default_admin_password:
                hashed_password = get_password_hash(default_admin_password)
                current_datetime = get_current_datetime_str()

                new_admin = AdminUser(
                    username=default_admin_username,
                    password_hash=hashed_password,
                    creation_date=current_datetime,
                    last_login=current_datetime,
                    is_two_factor_enabled=False,
                )
                session.add(new_admin)
                # Não comite ainda, comitaremos tudo junto no final para atomicidade.
                print(f"Usuário admin '{default_admin_username}' criado com sucesso!")
            else:
                print("DEFAULT_ADMIN_USERNAME ou DEFAULT_ADMIN_PASSWORD não configurados ou vazios. Não foi possível criar admin padrão.")
        else:
            print(f"Usuário admin '{default_admin_username}' já existe. Nenhuma ação necessária.")


        # --- Popular Employees Padrão (Lógica ajustada) ---
        print("Verificando e criando Employees (personagens) padrão...")
        for emp_data_raw in REQUIRED_EMPLOYEES_DATA:
            employee_name = emp_data_raw.get("employee_name")

            # Verifica se o funcionário já existe pelo employee_name (campo único)
            existing_employee = session.query(Employee).filter_by(employee_name=employee_name).first()

            if not existing_employee:
                # Cria uma nova instância do modelo Employee diretamente do dicionário
                new_employee = Employee(
                    employee_name=employee_name,
                    employee_script=emp_data_raw.get("employee_script"),
                    ia_name=emp_data_raw.get("ia_name"),
                    endpoint_url=emp_data_raw.get("endpoint_url"),
                    endpoint_key=emp_data_raw.get("endpoint_key"),
                    headers_template=emp_data_raw.get("headers_template"),
                    body_template=emp_data_raw.get("body_template"),
                    # Adicione outros campos se o seu modelo Employee os tiver e não forem auto-gerados
                    # Ex: creation_date=get_current_datetime_str(),
                )
                session.add(new_employee)
                print(f"Criando registro de funcionário mínimo: {employee_name}")
            else:
                print(f"Registro de funcionário mínimo já existe: {employee_name}")
        
        # Comita todas as alterações (admin e employees) de uma vez no final
        session.commit() 
        print("População de dados iniciais concluída.")

    except Exception as e:
        session.rollback() # Em caso de erro, reverte TODAS as alterações
        print(f"Erro ao popular dados iniciais: {e}")
        # Importante: Re-lançar a exceção para que o comando Docker saia com erro
        # e você saiba que a população falhou.
        raise 
    finally:
        session.close()

if __name__ == "__main__":
    populate_initial_data()