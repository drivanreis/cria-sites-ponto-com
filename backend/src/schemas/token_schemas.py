# File: backend/src/schemas/token_schemas.py

from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer" # O tipo de token, geralmente "bearer"

class TokenData(BaseModel):
    # Este schema reflete o payload que esperamos dentro do JWT
    id: int
    username: str # O identificador de login (username para admin, email/telefone para user)
    # >>> CORREÇÃO/NOVIDADE: Adicionado campo 'email' opcional no TokenData <<<
    # Ele será preenchido na decodificação do token se for user_type='user' e o username for um email.
    email: Optional[str] = None
    user_type: str # Para identificar se é 'admin' ou 'user'