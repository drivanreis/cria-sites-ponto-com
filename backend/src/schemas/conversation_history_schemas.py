# File: backend/src/schemas/conversation_history_schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any # Dict e Any são usados em BriefingRequest, não diretamente nos schemas de history
from datetime import datetime # Importação não utilizada diretamente para tipagem dos campos.

class ConversationHistoryBase(BaseModel):
    sender_type: str = Field(..., max_length=50, description="Tipo do remetente: 'user' ou o nome do employee (ex: 'Entrevistador Pessoal').")
    message_content: str

class ConversationHistoryCreate(ConversationHistoryBase):
    briefing_id: int # Adiciona briefing_id ao schema de criação

class ConversationHistoryRead(ConversationHistoryBase): # Usado para leitura (resposta da API)
    id: int
    briefing_id: int
    timestamp: str # Mudado para str para corresponder ao modelo do DB

    class Config:
        from_attributes = True

class ConversationHistoryUpdate(BaseModel):
    message_content: Optional[str] = None # Apenas o conteúdo da mensagem pode ser atualizado

# --- Schemas de Requisição para as Rotas (mantidos como estão) ---

class ChatRequest(BaseModel):
    """Schema para a requisição de chat com um Employee."""
    employee_name: str = Field(..., description="O nome do Employee (personagem) com quem conversar.")
    user_message: str = Field(..., description="A mensagem enviada pelo usuário.")

class BriefingRequest(BaseModel):
    """Schema para a requisição de compilação de briefing."""
    employee_name: str = Field(..., description="O nome do Employee (personagem) que irá compilar o briefing (ex: 'Assistente de Palco').")
    # Poderíamos adicionar outros campos, como um limite de histórico específico para o briefing, se necessário.