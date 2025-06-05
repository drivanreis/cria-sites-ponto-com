# File: backend/src/models/briefing_models.py

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON # Usar JSON do MySQL/MariaDB para o conteúdo
from ..db.database import Base # Importar a Base declarativa

class Briefing(Base):
    __tablename__ = 'briefings'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False) # Vincula o briefing ao usuário
    title = Column(String(255), nullable=False) # Título do briefing (ex: "Meus Hobbies", "Projeto E-commerce X")
    content = Column(JSON, nullable=True) # Conteúdo estruturado do briefing gerado/editado (Pode ser NULL no início)
    status = Column(String(50), default='Em Construção', nullable=False) # Status (ex: 'Em Construção', 'Pronto para Revisão', 'Finalizado')
    development_roteiro = Column(JSON, nullable=True) # Roteiro/orçamento manual do administrador (JSON)
    creation_date = Column(String(19), nullable=False) # Data de criação do briefing
    update_date = Column(String(19), nullable=True) # Data da última alteração
    last_edited_by = Column(String(5), nullable=True) # Quem fez a última edição (user_type: 'user' ou 'admin')

    # Define o relacionamento com a tabela users
    user = relationship("User", back_populates="briefings")

    # Define o relacionamento com o histórico de conversas (um briefing tem muitas mensagens)
    conversation_histories = relationship(
        "ConversationHistory",
        back_populates="briefing",
        cascade="all, delete-orphan" # Deleta o histórico se o briefing for deletado
    )

    # Garante que a combinação user_id e title seja única
    __table_args__ = (UniqueConstraint('user_id', 'title', name='_user_title_uc'),)

    def __repr__(self):
        return f"<Briefing(id={self.id}, user_id={self.user_id}, title='{self.title}', status='{self.status}')>"