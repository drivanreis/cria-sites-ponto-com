# File: backend/src/models/conversation_history.py
# Modelo SQLAlchemy para a tabela conversation_history.

from sqlalchemy import Column, Integer, String, Text, DateTime, text, ForeignKey
from ..db.database import Base
from ..models.briefing import Briefing
from sqlalchemy.orm import relationship


class ConversationHistory(Base):
    __tablename__ = 'conversation_history'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    briefing_id = Column(Integer, ForeignKey('briefings.id')) # Vincula a mensagem ao briefing
    speaker_type = Column(String(10)) # Quem falou ('user' ou 'bot')
    speaker_role_name = Column(String(100), nullable=True) # Nome do papel da IA (se for 'bot')
    timestamp = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    text = Column(Text) # O conteúdo da mensagem

    
    briefing = relationship("src.models.briefing.Briefing", backref="conversation_history")


    def __repr__(self):
        return f"<ConversationHistory(id={self.id}, briefing_id={self.briefing_id}, speaker_type='{self.speaker_type}')>"