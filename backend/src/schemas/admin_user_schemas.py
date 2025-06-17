# File: backend/src/schemas/admin_user_schemas.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from src.utils.validate_password import validate_password_complexity

# Esquema Base para AdminUser
class AdminUserBase(BaseModel):
    username: str = Field(..., max_length=255)

# Esquema para criação de um novo AdminUser (inclui a senha em texto claro)
class AdminUserCreate(AdminUserBase):
    password: str = Field(..., min_length=6, max_length=255) 

    @field_validator('password')
    @classmethod
    def validate_password_field(cls, value: str) -> str:
        # Chama a função de validação externa
        return validate_password_complexity(value)
    
# Esquema para atualização de um AdminUser existente (todos os campos são opcionais)
class AdminUserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6, max_length=255) 
    is_two_factor_enabled: Optional[bool] = None

    @field_validator('password')
    @classmethod
    def validate_password_complexity_for_update(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        # Reutiliza o validador de complexidade da criação
        return validate_password_complexity(value)

# Esquema para representação de um AdminUser no banco de dados (saída da API)
# CORREÇÃO: Renomeado AdminUserInDB para AdminUserRead para clareza
class AdminUserRead(AdminUserBase):
    id: int
    creation_date: str # Conforme o modelo (String(19))
    last_login: Optional[str] = None # Conforme o modelo (String(19))
    
    # Estes campos são para uso interno ou para o próprio admin ao gerenciar seu perfil
    two_factor_secret: Optional[str] = None # O segredo pode ser nulo se 2FA não ativado
    is_two_factor_enabled: bool # Indica se 2FA está ativado

    class Config:
        # Permite que o Pydantic leia dados de objetos ORM (como os do SQLAlchemy)
        from_attributes = True # Para Pydantic V2 (equivalente a orm_mode = True em Pydantic V1)