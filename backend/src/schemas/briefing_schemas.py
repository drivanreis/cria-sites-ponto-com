# File: backend/src/schemas/briefing_schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime # Esta importação não é mais usada para tipagem de campos, mas pode ser útil para funções de data.

# Importar o schema de histórico de conversas
from src.schemas.conversation_history_schemas import ConversationHistoryRead 

# Reutilizando os Schemas existentes
class BriefingBase(BaseModel):
    title: str = Field(..., max_length=255)
    status: str = Field(default="Rascunho", max_length=50)
    content: Optional[Dict[str, Any]] = None # JSONField no DB, Dict[str, Any] no Pydantic

class BriefingCreate(BriefingBase):
    pass # Este schema é bom para criação, pois BriefingBase já define os campos básicos.

class BriefingUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    # >>> NOVIDADE: Adicionado development_roteiro para permitir atualização <<<\n
    development_roteiro: Optional[Dict[str, Any]] = None
    # last_edited_by não deve ser um campo de entrada para o cliente,
    # será preenchido automaticamente pelo backend.


class BriefingRead(BriefingBase):
    id: int
    user_id: int
    creation_date: str # Mudado para str para corresponder ao modelo do DB
    update_date: Optional[str] = None # Mudado para str
    last_edited_by: Optional[str] = None
    # >>> NOVIDADE: Adicionado development_roteiro ao schema de leitura <<<\n
    development_roteiro: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True # ou orm_mode = True para Pydantic < v2


# NOVO SCHEMA: Briefing com histórico de conversas
class BriefingWithHistoryRead(BriefingRead):
    conversation_history: List[ConversationHistoryRead] = []