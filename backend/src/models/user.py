# File: backend/src/models/user.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, text
from sqlalchemy.dialects.mysql import JSON # Usar JSON do MySQL/MariaDB
from ..db.database import Base # Importar a Base declarativa

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=True) # Permitir NULL para login social sem email local
    email_verified = Column(Boolean, default=False)
    phone_number = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=True) # Presente apenas para contas com login local
    name = Column(String(255))
    google_id = Column(String(255), unique=True, nullable=True) # ID único do Google para login social
    github_id = Column(String(255), unique=True, nullable=True) # ID único do GitHub para login social
    two_factor_secret = Column(String(255), nullable=True) # Armazena o segredo para 2FA TOTP
    is_two_factor_enabled = Column(Boolean, default=False)
    status = Column(String(50), default='active') # ex: 'active', 'blocked', 'deleted'
    creation_date = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    last_login = Column(DateTime, nullable=True)

    # __repr__ e outros métodos podem ser adicionados para melhor depuração se necessário
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"