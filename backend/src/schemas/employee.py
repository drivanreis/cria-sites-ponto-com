# File: backend/src/schemas/employee.py

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

# Esquema Base para Employee, contendo os campos que são sempre retornados
# e que podem ser a base para criação/atualização.
class EmployeeBase(BaseModel):
    role_name: str = Field(..., max_length=100) # Obrigatório
    display_name: str = Field(..., max_length=100) # Obrigatório
    ai_service_name: str = Field(..., max_length=100) # Obrigatório
    endpoint: str = Field(..., max_length=255) # Obrigatório
    model: str = Field(..., max_length=100) # Obrigatório
    api_key_env_var_name: str = Field(..., max_length=100) # Obrigatório
    initial_pre_prompt: str # Text é mapeado para str no Pydantic
    context_instructions: Optional[str] = None # Opcional no modelo (nullable=True)

# Esquema para criação de um novo Employee
class EmployeeCreate(EmployeeBase):
    pass # Herda todos os campos obrigatórios de EmployeeBase

# Esquema para atualização de um Employee existente (todos os campos são opcionais)
class EmployeeUpdate(BaseModel):
    role_name: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, max_length=100)
    ai_service_name: Optional[str] = Field(None, max_length=100)
    endpoint: Optional[str] = Field(None, max_length=255)
    model: Optional[str] = Field(None, max_length=100)
    api_key_env_var_name: Optional[str] = Field(None, max_length=100)
    initial_pre_prompt: Optional[str] = None
    context_instructions: Optional[str] = None

# Esquema para representação de um Employee no banco de dados (saída da API)
class EmployeeInDB(EmployeeBase):
    id: int
    # Campos que são gerados automaticamente ou gerenciados pelo backend
    creation_date: datetime
    update_date: Optional[datetime] = None # Opcional no modelo (nullable=True)

    class Config:
        from_attributes = True # Pydantic v2 (substitui orm_mode = True)
        # Permite que o Pydantic leia diretamente dos objetos do SQLAlchemy (ORM)