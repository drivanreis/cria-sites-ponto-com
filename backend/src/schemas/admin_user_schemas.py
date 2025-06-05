# File: backend/src/schemas/admin_user_schemas.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re # Para validação de Regex em caracteres especiais da senha

# Esquema Base para AdminUser
class AdminUserBase(BaseModel):
    username: str = Field(..., max_length=255)

# Esquema para criação de um novo AdminUser (inclui a senha em texto claro)
class AdminUserCreate(AdminUserBase):
    # CORREÇÃO: Aumentar min_length para 8 (ou mais) e max_length para 255 (ou mais)
    # para permitir senhas mais longas e seguras.
    password: str = Field(..., min_length=8, max_length=255) 

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, value: str) -> str:
        if len(value) < 8: # Reforça o min_length também no validador
            raise ValueError('A senha deve ter pelo menos 8 caracteres.')
        if not any(char.isdigit() for char in value):
            raise ValueError('A senha deve conter pelo menos um número.')
        if not any(char.isupper() for char in value):
            raise ValueError('A senha deve conter pelo menos uma letra maiúscula.')
        if not any(char.islower() for char in value):
            raise ValueError('A senha deve conter pelo menos uma letra minúscula.')
        
        # O seu regex estava bom, apenas uma pequena melhoria para incluir mais caracteres comuns.
        # Use r'[]' para caracteres especiais.
        special_chars_pattern = r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]'
        if not re.search(special_chars_pattern, value):
            raise ValueError(f'A senha deve conter pelo menos um caractere especial: {special_chars_pattern.replace("[", "").replace("]", "")}.')
        return value

# Esquema para atualização de um AdminUser existente (todos os campos são opcionais)
class AdminUserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=255)
    # CORREÇÃO: Manter consistência com a criação, permitindo senhas mais longas na atualização
    password: Optional[str] = Field(None, min_length=8, max_length=255) 
    # Adicionado 2FA update (opcional)
    is_two_factor_enabled: Optional[bool] = None


    @field_validator('password')
    @classmethod
    def validate_password_complexity_for_update(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        # Reutiliza o validador de complexidade da criação
        return AdminUserCreate.validate_password_complexity(value)

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