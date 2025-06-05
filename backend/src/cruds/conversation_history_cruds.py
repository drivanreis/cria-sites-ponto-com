# File: backend/src/cruds/conversation_history_cruds.py

from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from src.models.conversation_history_models import ConversationHistory
from src.schemas.conversation_history_schemas import ConversationHistoryCreate
from src.utils.datetime_utils import get_current_datetime_str # Para o timestamp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_conversation_entry(db: Session, entry: ConversationHistoryCreate) -> ConversationHistory:
    """
    Cria um novo registro de histórico de conversa.
    """
    logger.info(f"Criando entrada de conversa para briefing_id: {entry.briefing_id} - Remetente: {entry.sender_type}")
    db_entry = ConversationHistory(
        briefing_id=entry.briefing_id,
        sender_type=entry.sender_type,
        message_content=entry.message_content,
        timestamp=get_current_datetime_str() # Preenche automaticamente o timestamp
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    logger.info(f"Entrada de conversa ID {db_entry.id} criada com sucesso.")
    return db_entry

def get_conversation_entry(db: Session, entry_id: int) -> Optional[ConversationHistory]:
    """
    Retorna um registro de histórico de conversa pelo seu ID.
    """
    logger.info(f"Buscando entrada de conversa com ID: {entry_id}")
    return db.query(ConversationHistory).filter(ConversationHistory.id == entry_id).first()

def get_conversation_history_by_briefing_id(db: Session, briefing_id: int, limit: int = 20) -> List[ConversationHistory]:
    """
    Retorna o histórico de conversas para um briefing específico,
    ordenado por timestamp e limitado.
    O histórico é retornado em ordem cronológica ascendente (do mais antigo ao mais novo).
    """
    logger.info(f"Buscando histórico de conversa para briefing_id: {briefing_id}, limitado a {limit} mensagens.")
    return (
        db.query(ConversationHistory)
        .filter(ConversationHistory.briefing_id == briefing_id)
        .order_by(ConversationHistory.id.asc()) # Ou .timestamp.asc() se timestamp for mais confiável para ordem
        .limit(limit)
        .all()
    )

def get_all_conversation_history(db: Session, skip: int = 0, limit: int = 100) -> List[ConversationHistory]:
    """
    Retorna todo o histórico de conversas (para uso administrativo/debugging).
    """
    logger.info(f"Buscando todo o histórico de conversa (admin view), skip: {skip}, limit: {limit}.")
    return db.query(ConversationHistory).offset(skip).limit(limit).all()