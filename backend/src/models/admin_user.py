# File: backend/src/models/admin_user.py

from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from backend.src.models.base import Base # Importar a Base declarativa

class AdminUser(Base):
    __tablename__ = 'admin_users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), unique=True) # Nome de usuário para login administrativo
    password_hash = Column(String(255)) # Hash da senha administrativa
    name = Column(String(255), nullable=True)
    role = Column(String(50), default='admin') # Define o papel do administrador, ex: 'admin'
    creation_date = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    last_login = Column(TIMESTAMP, nullable=True)

    def __repr__(self):
        return f"<AdminUser(id={self.id}, username='{self.username}', role='{self.role}')>"