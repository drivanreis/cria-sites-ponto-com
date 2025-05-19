# File: backend/src/models/conversation_history.py
# Modelo SQLAlchemy para a tabela conversation_history.

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, text, ForeignKey
# Importar a Base declarativa - O caminho correto agora é a partir de 'src',
# assumindo que /app está no sys.path e /app/src é o pacote raiz.
from ..db.database import Base

# Importar o modelo Briefing para definir o relacionamento (usaremos 'src' como raiz)
# from src.models.briefing import Briefing


class ConversationHistory(Base):
    __tablename__ = 'conversation_history'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    briefing_id = Column(Integer, ForeignKey('briefings.id')) # Vincula a mensagem ao briefing
    speaker_type = Column(String(10)) # Quem falou ('user' ou 'bot')
    speaker_role_name = Column(String(100), nullable=True) # Nome do papel da IA (se for 'bot')
    text = Column(Text) # O conteúdo da mensagem
    timestamp = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP')) # Linha onde o erro estava ocorrendo

    # Define o relacionamento de volta para Briefing (usando string para evitar problema de importação circular)
    # briefing = relationship("src.models.briefing.Briefing", backref="conversation_history")


    def __repr__(self):
        return f"<ConversationHistory(id={self.id}, briefing_id={self.briefing_id}, speaker_type='{self.speaker_type}')>"