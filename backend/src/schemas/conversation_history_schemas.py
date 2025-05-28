# File: backend/src/schemas/conversation_history.py

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

# Esquema Base para ConversationHistory, contendo os campos comuns
# que podem ser usados para entrada e saída.
class ConversationHistoryBase(BaseModel):
    briefing_id: int # Obrigatório, conforme model
    speaker_type: str = Field(..., max_length=30) # Obrigatório, conforme model
    text: str # Obrigatório, conforme model (Text é mapeado para str no Pydantic)

# Esquema para criação de um novo registro de ConversationHistory
class ConversationHistoryCreate(ConversationHistoryBase):
    pass # Herda todos os campos obrigatórios de ConversationHistoryBase

# Esquema para atualização de um registro de ConversationHistory (todos os campos são opcionais)
class ConversationHistoryUpdate(BaseModel):
    briefing_id: Optional[int] = None
    speaker_type: Optional[str] = Field(None, max_length=30)
    text: Optional[str] = None

# Esquema para representação de um registro de ConversationHistory no banco de dados (saída da API)
class ConversationHistoryInDB(ConversationHistoryBase):
    id: int
    timestamp: datetime # Gerado automaticamente pelo banco de dados

    class Config:
        from_attributes = True # Pydantic v2 (substitui orm_mode = True)
        # Permite que o Pydantic leia diretamente dos objetos do SQLAlchemy (ORM)