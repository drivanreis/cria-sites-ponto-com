# File: backend/src/schemas/token.py

from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer" # O tipo de token, geralmente "bearer"

class TokenData(BaseModel):
    # Este schema reflete o payload que esperamos dentro do JWT
    # id e username são obrigatórios no payload do token para AdminUser
    id: int
    username: str
    user_type: str # Para identificar se é 'admin' ou 'user'