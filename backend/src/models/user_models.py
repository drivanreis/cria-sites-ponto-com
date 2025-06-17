# File: /backend/src/models/user_models.py

from sqlalchemy import Column, Integer, String, Boolean # Removido DateTime, text
from sqlalchemy.orm import relationship
from ..db.database import Base # Importar a Base declarativa

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=True) # Permitir NULL para login social sem email local
    email_verified = Column(Boolean, default=False)
    phone_number = Column(String(20), unique=True, nullable=True) # +357 (15) 98765-4321 / +55 (85) 98765-4321
    password_hash = Column(String(255), nullable=True) # Presente apenas para contas com login local
    nickname = Column(String(30), nullable=False) # Assumindo que o nome é obrigatório para um usuário
    google_id = Column(String(255), unique=True, nullable=True) # ID único do Google para login social
    github_id = Column(String(255), unique=True, nullable=True) # ID único do GitHub para login social
    two_factor_secret = Column(String(255), nullable=True) # Armazena o segredo para 2FA TOTP
    is_two_factor_enabled = Column(Boolean, default=False)
    status = Column(String(50), default='active') # ex: 'active', 'blocked', 'deleted'
    creation_date = Column(String(19), nullable=False) # Data de criação, será preenchida pelo CRUD
    last_login = Column(String(19), nullable=True) # Último login, será preenchido pelo CRUD

    briefings = relationship("Briefing", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', nickname='{self.nickname}', last_login='{self.last_login}')>"