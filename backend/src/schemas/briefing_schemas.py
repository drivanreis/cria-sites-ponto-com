# File: backend/src/schemas/briefing.py

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any # Importar Any para campos JSON

# Esquema Base para Briefing, contendo os campos comuns
# que podem ser usados para entrada e saída.
class BriefingBase(BaseModel):
    user_id: int # Obrigatório, conforme model
    title: Optional[str] = Field("Meus Hobbes", max_length=255) # Opcional, com default do modelo
    content: Any # JSON do SQLAlchemy mapeia para Any ou dict no Pydantic.
                 # Se o JSON tiver uma estrutura conhecida, pode usar um Pydantic Model aninhado aqui.
                 # Por simplicidade, usamos Any.
    status: Optional[str] = Field("Em Construção", max_length=50) # Opcional, com default do modelo
    development_roteiro: Optional[Any] = None # Opcional, JSON
    last_edited_by: Optional[str] = Field(None, max_length=50) # Opcional

# Esquema para criação de um novo Briefing
class BriefingCreate(BriefingBase):
    # Todos os campos necessários para criação já estão em BriefingBase,
    # mas aqui podemos torná-los explicitamente obrigatórios se quisermos
    # sobrepor os defaults (ex: title sem default)
    # Exemplo: title: str = Field(..., max_length=255) se você quiser que seja obrigatório na criação

    # Para seguir a lógica do modelo, onde title e status têm default,
    # BriefingBase já está bom.
    pass


# Esquema para atualização de um Briefing existente (todos os campos são opcionais)
class BriefingUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[Any] = None
    status: Optional[str] = Field(None, max_length=50)
    development_roteiro: Optional[Any] = None
    last_edited_by: Optional[str] = Field(None, max_length=50)
    # user_id não deve ser atualizado diretamente via este endpoint

# Esquema para representação de um Briefing no banco de dados (saída da API)
class BriefingInDB(BriefingBase):
    id: int
    creation_date: datetime
    update_date: Optional[datetime] = None # Opcional no modelo (nullable=True)

    class Config:
        from_attributes = True # Pydantic v2 (substitui orm_mode = True)
        # Permite que o Pydantic leia diretamente dos objetos do SQLAlchemy (ORM)