# File: backend/src/models/conversation_history_models.py

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..db.database import Base


class ConversationHistory(Base):
    __tablename__ = 'conversation_histories'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    briefing_id = Column(Integer, ForeignKey('briefings.id'), nullable=False) # Chave estrangeira para o briefing
    sender_type = Column(String(30), nullable=False, default='User') # Tipo do remetente: 'users.nickname' ou 'employees.employee_name'
    message_content = Column(Text, nullable=False) # Conteúdo da mensagem. Usar Text para mensagens longas.
    timestamp = Column(String(19), nullable=False) # Data e hora da mensagem

    # Relacionamento com a tabela de briefings
    briefing = relationship("Briefing", back_populates="conversation_histories")

    def __repr__(self):
        return f"<ConversationHistory(id={self.id}, briefing_id={self.briefing_id}, sender_type='{self.sender_type}', timestamp='{self.timestamp}')>"