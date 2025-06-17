# File: backend/src/schemas/employee_schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Any

class EmployeeRead(BaseModel):
    id: int
    employee_name: str
    employee_script: Any
    ia_name: str
    endpoint_url: str
    endpoint_key: str
    headers_template: Any
    body_template: Any
    last_update: Optional[str] = None

    class Config:
        from_attributes = True

# --- Schema para Atualização (PUT) ---
# Este schema define os campos que PODEM ser enviados em uma requisição PUT.
# Note que 'employee_name' NÃO está presente aqui, garantindo que não possa ser atualizado.
# Todos os campos são Optional, pois em um PUT, o cliente só envia o que deseja alterar.
class EmployeeUpdate(BaseModel):
    employee_script: Optional[Any] = Field(None, description="Roteiro do personagem. (JSON)")
    ia_name: Optional[str] = Field(None, max_length=30, description="Nome do assistente de IA 'ator'.")
    endpoint_url: Optional[str] = Field(None, max_length=255, description="URL base da API de IA.")
    endpoint_key: Optional[str] = Field(None, max_length=255, description="A chave da API.")
    headers_template: Optional[Any] = Field(None, description="Template dos cabeçalhos da requisição. (JSON)")
    body_template: Optional[Any] = Field(None, description="Template do corpo da requisição. (JSON)")
    # last_update não precisa estar aqui, pois será gerado/atualizado no backend.
    # Removi a linha que você tinha no seu último upload para este campo
    # last_update: Optional[str] = None

# --- Schema para Criação Interna (para a Inicialização) ---
# Este schema é usado para validar os dados na função de inicialização da aplicação,
# garantindo que os registros iniciais estejam completos e corretos.
# Inclui employee_name pois ele é mandatório na criação.
class EmployeeCreateInternal(BaseModel):
    employee_name: str = Field(..., max_length=30, description="Nome do personagem. (Obrigatório)")
    employee_script: Any = Field(..., description="Roteiro do personagem. (Obrigatório)")
    ia_name: str = Field(..., max_length=30, description="Nome do assistente de IA 'ator'. (Obrigatório)")
    endpoint_url: str = Field(..., max_length=255, description="URL base da API de IA. (Obrigatório)")
    endpoint_key: str = Field(..., max_length=255, description="A chave da API. (Obrigatório)")
    headers_template: Any = Field(..., description="Template dos cabeçalhos da requisição. (Obrigatório)")
    body_template: Any = Field(..., description="Template do corpo da requisição. (Obrigatório)")
    # last_update não é incluído aqui, pois é um campo gerenciado pelo backend.
    # Removi a linha que você tinha no seu último upload para este campo
    # last_update: Optional[str] = None