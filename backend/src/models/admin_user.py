# File: backend/src/models/admin_user.py

from sqlalchemy import Column, Integer, String, Boolean
from ..db.database import Base # Importar a Base declarativa

class AdminUser(Base):
    __tablename__ = 'admin_users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), nullable=False, unique=True) # Nome de usuário para login administrativo
    password_hash = Column(String(255), nullable=False) # Hash da senha administrativa
    two_factor_secret = Column(String(255), nullable=True) # Armazena o segredo para 2FA TOTP
    is_two_factor_enabled = Column(Boolean, default=False)
    creation_date = Column(String(19), nullable=False)
    last_login = Column(String(19), nullable=True)

    def __repr__(self):
        return f"<AdminUser(id={self.id}, username='{self.username}', last_login='{self.last_login}')>"
    