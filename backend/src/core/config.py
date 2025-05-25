# File: backend/src/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # >>> CORREÇÃO: Duas variáveis de expiração de token <<<
    ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Curto para admins
    USER_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120 # Mais longo para usuários comuns (ex: 2 horas)

    DEFAULT_ADMIN_USERNAME: Optional[str] = None
    DEFAULT_ADMIN_PASSWORD: Optional[str] = None


settings = Settings()