# File: backend/src/cruds/conversation_history.py

from sqlalchemy.orm import Session
from typing import List, Optional # Importar Optional

from src.models.conversation_history_models import ConversationHistory
from src.schemas.conversation_history_schemas import ConversationHistoryCreate, ConversationHistoryUpdate
# from src.utils.datetime_utils import get_current_datetime_brasilia # Remover se não for mais usada aqui

def get_conversation_message(db: Session, message_id: int) -> Optional[ConversationHistory]:
    return db.query(ConversationHistory).filter(ConversationHistory.id == message_id).first()

def get_conversation_history_by_briefing(db: Session, briefing_id: int, skip: int = 0, limit: int = 100) -> List[ConversationHistory]:
    # Order by timestamp to get the conversation in chronological order
    return db.query(ConversationHistory).filter(ConversationHistory.briefing_id == briefing_id).order_by(ConversationHistory.timestamp).offset(skip).limit(limit).all()

def create_conversation_message(db: Session, message: ConversationHistoryCreate) -> ConversationHistory:
    db_message = ConversationHistory(
        briefing_id=message.briefing_id,
        speaker_type=message.speaker_type,
        # REMOVIDO: speaker_role_name - Este campo não existe no modelo ConversationHistory
        text=message.text,
        # REMOVIDO: timestamp - Ele é definido por server_default=CURRENT_TIMESTAMP no modelo
        # Não é necessário passar get_current_datetime_brasilia() aqui.
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def update_conversation_message(db: Session, message_id: int, message: ConversationHistoryUpdate) -> Optional[ConversationHistory]:
    db_message = db.query(ConversationHistory).filter(ConversationHistory.id == message_id).first()
    if db_message:
        for key, value in message.dict(exclude_unset=True).items():
            # Apenas atribui o valor se o campo existir no modelo ConversationHistory
            if hasattr(db_message, key):
                setattr(db_message, key, value)
            # REMOVIDO: Lógica para updated_at, pois o modelo ConversationHistory não possui esse campo.
            # Se a coluna 'timestamp' fosse atualizada para refletir a modificação,
            # precisaríamos adicionar uma lógica específica para isso, mas geralmente
            # o timestamp de uma mensagem de histórico não é alterado após a criação.
            # Caso seja necessário ter um timestamp de atualização, adicione 'update_date'
            # ao modelo ConversationHistory e ao schema.
        
        db.commit()
        db.refresh(db_message)
    return db_message

def delete_conversation_message(db: Session, message_id: int) -> bool:
    db_message = db.query(ConversationHistory).filter(ConversationHistory.id == message_id).first()
    if db_message:
        db.delete(db_message)
        db.commit()
        return True
    return False