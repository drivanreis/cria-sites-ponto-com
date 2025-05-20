# File: backend/src/schemas/conversation_history.py

from datetime import datetime
from pydantic import BaseModel, Field

class ConversationHistoryBase(BaseModel):
    briefing_id: int
    speaker_type: str = Field(..., max_length=10) # 'user' or 'bot'
    speaker_role_name: str | None = Field(None, max_length=100) # e.g., "AI Assistant"
    text: str = Field(...)

class ConversationHistoryCreate(ConversationHistoryBase):
    pass

class ConversationHistoryUpdate(BaseModel):
    speaker_type: str | None = Field(None, max_length=10)
    speaker_role_name: str | None = Field(None, max_length=100)
    text: str | None = Field(None)

class ConversationHistoryInDB(ConversationHistoryBase):
    id: int
    timestamp: datetime # Note: This is managed by the DB's server_default

    class Config:
        orm_mode = True