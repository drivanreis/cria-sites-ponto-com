# File: backend/src/models/employee_models.py

from sqlalchemy import Column, Integer, String
from ..db.database import Base
from sqlalchemy.dialects.mysql import JSON

class Employee(Base): 
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender_type = Column(String(30), unique=True, nullable=False) # O nome personagem (Entrevistador Pessoal, etc.)
    employee_script = Column(JSON, nullable=False) # Roteiro do personagem
    ia_name = Column(String(30), nullable=False) # Nome do assistente de IA "ator" (ChatGPT, Gemini, DeepSeek)
    endpoint_url = Column(String(255), nullable=False) # URL base da API de IA
    endpoint_key = Column(String(255), nullable=False) # A chave da API
    headers_template = Column(JSON, nullable=False)
    body_template = Column(JSON, nullable=False)
    last_update = Column(String(19), nullable=True)

    def __repr__(self):
        return f"<Employee(id={self.id}, sender_type='{self.sender_type}', last_update='{self.last_update}')>"