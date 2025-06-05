# File: backend/src/schemas/user_schemas.py

from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator, ValidationInfo
from typing import Optional, Any
import re # Para validação de Regex no telefone

# Esquema Base com campos comuns para entrada e saída que refletem o modelo
# Usado para herança para evitar duplicação de campos
class UserBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    email: Optional[EmailStr] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20) # Corrigido max_length para 20 (modelo)

    # NOVIDADE: Validador para formato do telefone
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number_format(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        # Regex mais robusto para telefones brasileiros com ou sem DDI/DDD.
        # Ex: +5511987654321, 11987654321, 9876543210
        # Permite: + (opcional), 2 digitos (DDI opcional), 2 digitos (DDD opcional), 8-9 digitos (numero)
        # ^\\+?              -> Opcional +
        # (?:\\d{2})?        -> Opcional DDI (2 dígitos, não captura)
        # (?:\\d{2})?        -> Opcional DDD (2 dígitos, não captura)
        # \\d{8,9}$          -> Número (8 ou 9 dígitos no final)
        # Esta regex é mais flexível para números de telefone brasileiros com ou sem DDD/DDI.
        # Ajuste se precisar de um formato mais estrito (ex: apenas DDD com 2 digitos).
        phone_regex = r"^\+?(?:[0-9]{2})?(?:[0-9]{2})?[0-9]{8,9}$"
        
        if not re.fullmatch(phone_regex, value):
            raise ValueError("Formato de telefone inválido. Use apenas números e opcionalmente '+' no início.")
        
        return value


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
    def validate_password_complexity(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError('A senha deve ter pelo menos 6 caracteres.')
        if not re.search(r"[A-Z]", value):
            raise ValueError('A senha deve conter pelo menos uma letra maiúscula.')
        if not re.search(r"[a-z]", value):
            raise ValueError('A senha deve conter pelo menos uma letra minúscula.')
        if not re.search(r"[0-9]", value):
            raise ValueError('A senha deve conter pelo menos um dígito.')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError('A senha deve conter pelo menos um caractere especial.')
        return value


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
        # Reutilizar o validador de criação
        return UserCreate.validate_password_complexity(value) 


# Esquema para representação de usuário no banco de dados (saída da API)
# Corrigido o nome para UserRead e alinhado os tipos de data
class UserRead(UserBase):
    id: int
    email_verified: bool
    # password_hash: Optional[str] = None # REMOVIDO: NUNCA expor o hash da senha
    # two_factor_secret: Optional[str] = None # REMOVIDO: NUNCA expor o segredo 2FA
    google_id: Optional[str] = None
    github_id: Optional[str] = None
    is_two_factor_enabled: bool
    status: str
    # CORREÇÃO: Datas como string, conforme o modelo (String(19))
    creation_date: str # O modelo armazena como String(19)
    last_login: Optional[str] = None # O modelo armazena como String(19)

    class Config:
        # Permite que o Pydantic leia dados de objetos ORM (como os do SQLAlchemy)
        from_attributes = True # ou orm_mode = True em Pydantic V1