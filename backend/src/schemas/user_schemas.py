# File: backend/src/schemas/user.py

# >>> Importações atualizadas <<<
from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator # Importar model_validator e field_validator
from typing import Optional
import re # Para validação de Regex no telefone

# Esquema Base com campos comuns para entrada e saída (que existem no modelo)
class UserBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    email: Optional[EmailStr] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20) # Corrigido max_length para 20 (modelo)

    # >>> NOVIDADE: Validador para formato do telefone <<<
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number_format(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        # Regex básico para formato de telefone: + (opcional), 1 a 3 dígitos para código de país, 
        # seguido por 8 a 15 dígitos para o número. Pode ser ajustado conforme a necessidade.
        # Ex: +5511987654321 ou 11987654321
        # Usando regex mais permissivo para acomodar formatos variados, 
        # mas garantindo que sejam dígitos e talvez um '+' inicial.
        # Uma regex mais robusta para Brasil pode ser: r'^\+?(\d{2})?(\d{2})?\d{8,9}$'
        # Mas para ser genérico e evitar "qualquer besteira":
        if not re.fullmatch(r'^\+?\d{8,15}$', value): # Permite + e 8 a 15 dígitos
            raise ValueError('O número de telefone deve conter apenas dígitos, opcionalmente iniciado por "+", e ter entre 8 e 15 caracteres.')
        return value

# Esquema para criação de usuário (inclui a senha em texto claro)
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=16) # Senha é obrigatória na criação (ajustado para min_length 6 e max_length 16)

    # >>> NOVIDADE: Validadores de complexidade da senha (Copiado de AdminUserCreate) <<<
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

    # >>> NOVIDADE: Validador para garantir E-mail OU Telefone <<<
    @model_validator(mode='after') # Valida depois que os campos individuais foram validados
    def check_email_or_phone_number(self) -> 'UserCreate':
        # Esta validação se aplica apenas se nem google_id nem github_id forem fornecidos
        # Isso permite que usuários de social login não tenham email/telefone no primeiro momento,
        # MAS, se for um login tradicional, exige um.
        # Para social login, a coleta de email/telefone faltante deve ser no frontend/fluxo de onboarding.
        # PORÉM, A REGRA DE NEGÓCIO É QUE SEMPRE PRECISA TER UM CONTATO.
        # Então, vamos aplicar isso aqui, e o frontend que vai se virar para coletar,
        # seja no cadastro local, seja num post-social login.
        
        # A regra é: Se não houver google_id NEM github_id (ou seja, é um cadastro tradicional),
        # ENTÃO deve haver email OU phone_number.
        # Se você permitir que social logins *criem* um usuário sem email/phone_number,
        # então essa lógica precisaria ser movida para um validador CONDICIONAL
        # ou o schema de criação para social logins seria diferente.
        # No seu modelo, google_id e github_id são opcionais.
        # Para simplificar agora e garantir a regra de "precisa ter um contato",
        # vamos deixar essa validação de modelo, e o fluxo de login social,
        # se não fornecer email, terá que vir com um phone_number OU o fluxo terá que criar um user
        # com email/phone_number nulos (e depois pedir no onboarding).
        
        # Dada a conversa anterior, onde decidimos *precisar* de um contato para fins de comunicação,
        # esta validação *deve* ocorrer aqui, independentemente do tipo de login.
        # O fluxo de login social, se não fornecer email, *terá* que passar por uma etapa de coleta de telefone.
        if not self.email and not self.phone_number:
            raise ValueError('Pelo menos um e-mail ou número de telefone é obrigatório para contato.')
        return self


# Esquema para atualização de usuário (todos os campos são opcionais)
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    email: Optional[EmailStr] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6, max_length=16) # Ajustado min_length e max_length
    phone_number: Optional[str] = Field(None, max_length=20)

    # Aplicar o mesmo validador de complexidade à senha de atualização, se ela for fornecida
    @field_validator('password')
    @classmethod
    def validate_password_complexity_for_update(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return UserCreate.validate_password_complexity(value) # Reutilizar o validador de criação

    # >>> NOVIDADE: Validador para formato do telefone para updates <<<
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number_format_for_update(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        # Reutilizar o validador de formato base
        return UserBase.validate_phone_number_format(value)


# Esquema para representação de usuário no banco de dados (saída da API)
class UserInDB(UserBase):
    id: int
    email_verified: bool
    # >>> CORREÇÃO: Não expor password_hash e two_factor_secret <<<
    # password_hash: Optional[str] = None # REMOVIDO: NUNCA expor o hash da senha
    # two_factor_secret: Optional[str] = None # REMOVIDO: NUNCA expor o segredo 2FA
    google_id: Optional[str] = None
    github_id: Optional[str] = None
    is_two_factor_enabled: bool
    status: str
    # >>> CORREÇÃO: Datas como string, conforme modelo <<<
    creation_date: str 
    last_login: Optional[str] = None

    class Config:
        from_attributes = True # ATUALIZADO para Pydantic v2 (era orm_mode = True)