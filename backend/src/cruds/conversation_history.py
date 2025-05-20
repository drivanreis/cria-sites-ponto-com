# File: backend/src/cruds/conversation_history.py

from sqlalchemy.orm import Session
from typing import List

from src.models.conversation_history import ConversationHistory
from src.schemas.conversation_history import ConversationHistoryCreate, ConversationHistoryUpdate
from src.utils.datetime_utils import get_current_datetime_brasilia

def get_conversation_message(db: Session, message_id: int):
    return db.query(ConversationHistory).filter(ConversationHistory.id == message_id).first()

def get_conversation_history_by_briefing(db: Session, briefing_id: int, skip: int = 0, limit: int = 100) -> List[ConversationHistory]:
    # Order by timestamp to get the conversation in chronological order
    return db.query(ConversationHistory).filter(ConversationHistory.briefing_id == briefing_id).order_by(ConversationHistory.timestamp).offset(skip).limit(limit).all()

def create_conversation_message(db: Session, message: ConversationHistoryCreate) -> ConversationHistory:
    db_message = ConversationHistory(
        briefing_id=message.briefing_id,
        speaker_type=message.speaker_type,
        speaker_role_name=message.speaker_role_name,
        text=message.text,
        # timestamp is set by server_default in the model, no need to pass it here
        # but we could optionally pass get_current_datetime_brasilia() if we want
        # the application to control it explicitly rather than relying on DB default.
        # Sticking to the plan: DB handles server_default, get_current_datetime_brasilia
        # is for application logic where precise time setting is needed (e.g., specific CRUDs
        # or logging that are not covered by DB default).
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def update_conversation_message(db: Session, message_id: int, message: ConversationHistoryUpdate) -> ConversationHistory | None:
    db_message = db.query(ConversationHistory).filter(ConversationHistory.id == message_id).first()
    if db_message:
        for key, value in message.dict(exclude_unset=True).items():
            setattr(db_message, key, value)
        
        # Note: No updated_at for ConversationHistory in model. 
        # If needed, add it to the model and schema first.
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