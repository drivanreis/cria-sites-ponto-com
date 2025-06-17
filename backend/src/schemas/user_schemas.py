# File: backend/src/schemas/user_schemas.py

import re # Pode ser removido se não for usado para mais nada neste arquivo
from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator
from typing import Optional
from src.utils.validate_password import validate_password_complexity # Importa a validação de senha
from src.utils.validate_phone_number import validate_phone_number_format # Importa a validação de telefone

class UserBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    email: Optional[EmailStr] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20) # Corrigido max_length para 20 (modelo)

    # NOVIDADE: Validador para formato do telefone - AGORA CHAMANDO A FUNÇÃO EXTERNA
    @field_validator('phone_number')
    @classmethod
    def validate_user_phone_number_field(cls, value: Optional[str]) -> Optional[str]:
        # Chama a função de validação de telefone do arquivo utils
        return validate_phone_number_format(value)


# Esquema para criação de usuário (entrada da API)
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=255) # Senha é obrigatória na criação

    @model_validator(mode='after')
    def check_email_or_phone_number(self) -> 'UserCreate':
        if self.email is None and self.phone_number is None:
            raise ValueError('Pelo menos um email ou um número de telefone deve ser fornecido para o cadastro.')
        return self

    @field_validator('password')
    @classmethod
    def validate_password_field(cls, value: str) -> str:
        return validate_password_complexity(value)

# Esquema para atualização de usuário (entrada da API)
# Todos os campos são opcionais para permitir atualizações parciais
class UserUpdate(UserBase):
    name: Optional[str] = Field(None, min_length=3, max_length=255) # Nome pode ser atualizado e ser opcional
    password: Optional[str] = Field(None, min_length=6, max_length=255)
    
    # Aplicar o mesmo validador de complexidade à senha de atualização, se ela for fornecida
    @field_validator('password')
    @classmethod
    def validate_password_complexity_for_update(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return validate_password_complexity(value)

# Esquema para representação de usuário no banco de dados (saída da API)
# Corrigido o nome para UserRead e alinhado os tipos de data
class UserRead(UserBase):
    id: int
    email_verified: bool
    google_id: Optional[str] = None
    github_id: Optional[str] = None
    is_two_factor_enabled: bool
    status: str
    creation_date: str # O modelo armazena como String(19)
    last_login: Optional[str] = None # O modelo armazena como String(19)

    class Config:
        # Permite que o Pydantic leia dados de objetos ORM (como os do SQLAlchemy)
        from_attributes = True # ou orm_mode = True em Pydantic V1