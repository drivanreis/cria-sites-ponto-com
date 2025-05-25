# File: backend/src/cruds/user.py

from sqlalchemy.orm import Session
from typing import List, Optional
# >>> CORREÇÃO: Usar passlib.context para hashing de senhas <<<
from passlib.context import CryptContext
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
# >>> NOVIDADE: Importar get_current_datetime_str para datas <<<
from src.utils.datetime_utils import get_current_datetime_str

# Para hashear e verificar senhas (usando bcrypt como esquema, consistente com AdminUser)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funções CRUD ---

def get_user(db: Session, user_id: int) -> Optional[User]: # Adicionado tipo de retorno
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]: # Adicionado tipo de retorno
    return db.query(User).filter(User.email == email).first()

# >>> NOVIDADE: Adicionado get_user_by_phone_number <<<
def get_user_by_phone_number(db: Session, phone_number: str) -> Optional[User]:
    return db.query(User).filter(User.phone_number == phone_number).first()

# >>> NOVIDADE: Adicionado get_user_by_google_id <<<
def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    return db.query(User).filter(User.google_id == google_id).first()

# >>> NOVIDADE: Adicionado get_user_by_github_id <<<
def get_user_by_github_id(db: Session, github_id: str) -> Optional[User]:
    return db.query(User).filter(User.github_id == github_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

# Função para criar um novo usuário
def create_user(db: Session, user: UserCreate) -> User:
    # Hash da senha (se fornecida, pois user.password é None para social logins sem senha local)
    hashed_password = None
    if user.password: # Apenas hashear se a senha for fornecida (para login local)
        hashed_password = pwd_context.hash(user.password)
    
    current_datetime_str = get_current_datetime_str()

    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password, # Será None se não houver senha local
        phone_number=user.phone_number,
        # Campos de login social (google_id, github_id) serão None na criação via UserCreate
        # A lógica para preencher estes campos será em uma rota de autenticação social separada.
        # Campos de 2FA e status terão seus defaults do modelo (False, 'active')
        creation_date=current_datetime_str, # Preenche a data de criação
        last_login=None # Preenchido apenas no primeiro login
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Função para atualizar um usuário existente
def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]: # Corrigido tipo de retorno
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        # >>> CORREÇÃO: Usar model_dump(exclude_unset=True) para Pydantic v2 <<<
        update_data = user.model_dump(exclude_unset=True) 
        
        # Se a senha for atualizada, hashear
        if "password" in update_data and update_data["password"]:
            hashed_password = pwd_context.hash(update_data["password"])
            db_user.password_hash = hashed_password
            del update_data["password"] # Remover a senha em texto claro antes de iterar
        
        # Aplicar as atualizações restantes
        for key, value in update_data.items():
            # Excluímos 'password' pois já foi tratado
            # Não precisamos de 'full_name' para 'name' se o schema já usa 'name'
            # Não precisamos mais remover campos antigos, eles não virão do schema UserUpdate
            if hasattr(db_user, key): # Garante que o campo existe no modelo
                setattr(db_user, key, value)
        
        # last_login é atualizado em uma ação de login, não em um update genérico de perfil
        # creation_date nunca deve ser atualizado
        # two_factor_secret e is_two_factor_enabled devem ser atualizados via rotas específicas de 2FA.

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return db_user

# Função para deletar um usuário
def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# Função para verificar senha (para autenticação)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # >>> CORREÇÃO: Usar pwd_context para verificar a senha <<<
    return pwd_context.verify(plain_password, hashed_password)