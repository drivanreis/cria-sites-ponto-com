# File: backend/src/models/briefing.py

from sqlalchemy import Column, Integer, String, DateTime, text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON # Usar JSON do MySQL/MariaDB para o conteúdo e roteiro
from sqlalchemy.orm import relationship
from ..db.database import Base # Importar a Base declarativa

class Briefing(Base):
    __tablename__ = 'briefings'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id')) # Vincula o briefing ao usuário
    title = Column(String(255), unique=True, default='Meus Hobbes') # Tipo de briefing (ex: 'pessoal', 'empresarial')
    content = Column(JSON) # Conteúdo estruturado do briefing gerado/editado
    status = Column(String(50), default='Em Construção') # Status (ex: 'Em Construção', 'Pronto para Revisão')
    development_roteiro = Column(JSON, nullable=True) # Roteiro/orçamento manual do administrador
    creation_date = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    update_date = Column(DateTime, nullable=True) # Data da última alteração
    last_edited_by = Column(String(50), nullable=True) # Quem fez a última edição ('user' ou 'admin')

    # Define o relacionamento com a tabela users
    user = relationship("User", back_populates="briefings")

    # Define o relacionamento com o histórico de conversas (um briefing tem muitas mensagens)
    conversation_history = relationship(
        "ConversationHistory", 
        back_populates="briefing", 
        uselist=False, # Importante: Define como 1:1, garantindo que seja um único objeto, não uma lista
        cascade="all, delete-orphan" # Opcional: Deleta o histórico se o briefing for deletado
    )

    __table_args__ = (UniqueConstraint('user_id', 'title', name='_user_title_uc'),)

    def __repr__(self):
        return f"<Briefing(id={self.id}, user_id={self.user_id}, type='{self.type}', status='{self.status}')>"