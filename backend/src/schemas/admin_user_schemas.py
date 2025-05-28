# File: backend/src/schemas/admin_user.py

from datetime import datetime
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Optional

# Esquema Base para AdminUser
class AdminUserBase(BaseModel):
    username: str = Field(..., max_length=255)

# Esquema para criação de um novo AdminUser (inclui a senha em texto claro)
class AdminUserCreate(AdminUserBase):
    password: str = Field(..., min_length=6, max_length=16)

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, value: str) -> str:
        if not any(char.isdigit() for char in value):
            raise ValueError('A senha deve conter pelo menos um número.')
        if not any(char.isupper() for char in value):
            raise ValueError('A senha deve conter pelo menos uma letra maiúscula.')
        if not any(char.islower() for char in value):
            raise ValueError('A senha deve conter pelo menos uma letra minúscula.')
        special_chars = r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]'
        if not any(char in special_chars for char in value):
            raise ValueError(f'A senha deve conter pelo menos um caractere especial: {special_chars.replace("[", "").replace("]", "")}.')
        return value

# Esquema para atualização de um AdminUser existente (todos os campos são opcionais)
class AdminUserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6, max_length=16) 

    @field_validator('password')
    @classmethod
    def validate_password_complexity_for_update(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return AdminUserCreate.validate_password_complexity(value)

# Esquema para representação de um AdminUser no banco de dados (saída da API)
class AdminUserInDB(AdminUserBase):
    id: int
    creation_date: str
    last_login: Optional[str] = None
    # >>> NOVIDADE: Adicionados campos de 2FA para o esquema de saída <<<
    two_factor_secret: Optional[str] = None # O segredo pode ser nulo se 2FA não ativado
    is_two_factor_enabled: bool = False # Default para False, como no modelo

    class Config:
        from_attributes = True