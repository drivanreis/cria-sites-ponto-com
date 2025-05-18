# File: backend/src/models/briefing.py

from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey
from sqlalchemy.dialects.mysql import JSON # Usar JSON do MySQL/MariaDB para o conteúdo e roteiro
from sqlalchemy.orm import relationship
from backend.src.models.base import Base # Importar a Base declarativa

class Briefing(Base):
    __tablename__ = 'briefings'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id')) # Vincula o briefing ao usuário
    type = Column(String(50)) # Tipo de briefing (ex: 'pessoal', 'empresarial')
    content = Column(JSON) # Conteúdo estruturado do briefing gerado/editado
    status = Column(String(50), default='Em Construção') # Status (ex: 'Em Construção', 'Pronto para Revisão')
    development_roteiro = Column(JSON, nullable=True) # Roteiro/orçamento manual do administrador
    creation_date = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    update_date = Column(TIMESTAMP, nullable=True) # Data da última alteração
    last_edited_by = Column(String(50), nullable=True) # Quem fez a última edição ('user' ou 'admin')

    # Define o relacionamento com a tabela users
    user = relationship("User", backref="briefings")

    # Define o relacionamento com o histórico de conversas (um briefing tem muitas mensagens)
    conversation_history = relationship("ConversationHistory", backref="briefing", order_by="ConversationHistory.timestamp")

    def __repr__(self):
        return f"<Briefing(id={self.id}, user_id={self.user_id}, type='{self.type}', status='{self.status}')>"