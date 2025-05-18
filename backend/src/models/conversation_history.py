# File: backend/src/models/conversation_history.py

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, text, ForeignKey
from backend.src.models.base import Base # Importar a Base declarativa

class ConversationHistory(Base):
    __tablename__ = 'conversation_history'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    briefing_id = Column(Integer, ForeignKey('briefings.id')) # Vincula a mensagem ao briefing
    speaker_type = Column(String(10)) # Quem falou ('user' ou 'bot')
    speaker_role_name = Column(String(100), nullable=True) # Nome do papel da IA (se for 'bot')
    text = Column(Text) # O conteúdo da mensagem
    timestamp = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"<ConversationHistory(id={self.id}, briefing_id={self.briefing_id}, speaker_type='{self.speaker_type}')>"