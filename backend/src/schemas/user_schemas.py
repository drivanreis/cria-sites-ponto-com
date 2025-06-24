# File: backend/src/schemas/user_schemas.py

from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator
from typing import Optional
from src.utils.validate_password import validate_password_complexity
from src.utils.validate_phone_number import validate_phone_number_format

class UserBase(BaseModel):
    nickname: str = Field(..., min_length=3, max_length=255)
    email: Optional[EmailStr] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    google_id: Optional[str] = None
    github_id: Optional[str] = None

    @field_validator('phone_number')
    @classmethod
    def validate_user_phone_number_field(cls, value: Optional[str]) -> Optional[str]:
        if value:
            return validate_phone_number_format(value)
        return value

# Esquema para criação de usuário (entrada da API)
class UserCreate(UserBase):
    password: Optional[str] = Field(None, min_length=6, max_length=255)

    @model_validator(mode='after')
    def validate_creation_logic(self) -> 'UserCreate':
        if self.google_id or self.github_id:
            # Fluxo de login social
            if not self.nickname:
                raise ValueError('Nickname é obrigatório.')
            return self

        # Fluxo de cadastro manual
        if not self.email and not self.phone_number:
            raise ValueError('Pelo menos um email ou um número de telefone deve ser fornecido para o cadastro manual.')
        if not self.password:
            raise ValueError('Senha obrigatória no cadastro manual.')
        return self

    @field_validator('password')
    @classmethod
    def validate_password_field(cls, value: Optional[str]) -> Optional[str]:
        if value:
            return validate_password_complexity(value)
        return value

# Esquema para atualização de usuário (entrada da API)
class UserUpdate(UserBase):
    nickname: Optional[str] = Field(None, min_length=3, max_length=255)
    password: Optional[str] = Field(None, min_length=6, max_length=255)

    @field_validator('password')
    @classmethod
    def validate_password_complexity_for_update(cls, value: Optional[str]) -> Optional[str]:
        if value:
            return validate_password_complexity(value)
        return value

# Esquema para leitura de usuário (saída da API)
class UserRead(UserBase):
    id: int
    email_verified: bool
    is_two_factor_enabled: bool
    status: str
    creation_date: str
    last_login: Optional[str] = None

    class Config:
        from_attributes = True
