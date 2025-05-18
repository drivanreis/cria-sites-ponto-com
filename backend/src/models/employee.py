# File: backend/src/models/employee.py

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, text, UniqueConstraint
from backend.src.models.base import Base # Importar a Base declarativa

class Employee(Base): # Usando Employee pois representa os "funcionários" IA
    __tablename__ = 'employees' # Nome da tabela conforme contrato

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name = Column(String(100), unique=True) # O nome técnico/interno do papel (Entrevistador Pessoal, etc.)
    display_name = Column(String(100)) # Nome que será exibido na interface (editável)
    ai_service_name = Column(String(100)) # Nome do serviço de IA "ator" (ChatGPT, Gemini, DeepSeek)
    endpoint = Column(String(255)) # URL base da API de IA
    model = Column(String(100)) # Nome do modelo específico da API
    api_key_env_var_name = Column(String(100)) # Nome da variável de ambiente com a chave da API
    initial_pre_prompt = Column(Text) # O texto do Pré-Prompt
    context_instructions = Column(Text, nullable=True) # Instruções contextuais adicionais
    creation_date = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    update_date = Column(TIMESTAMP, nullable=True)

    # Adicionar UniqueConstraint caso precise de unicidade composta no futuro, mas role_name já é unique

    def __repr__(self):
        return f"<Employee(id={self.id}, role_name='{self.role_name}', display_name='{self.display_name}')>"