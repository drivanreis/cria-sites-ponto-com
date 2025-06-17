# File: backend/src/services/character_service.py (REVISADO)

from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import logging
from fastapi import HTTPException, status

from src.cruds import employee_cruds
from src.models.conversation_history_models import ConversationHistory
from src.services import connect_ai_service # Importa o novo serviço de conexão de IA


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Serviço de Interação com Personagens de IA ---

async def get_ai_response_for_character(
    db: Session,
    employee_name: str,
    user_message: str, # Esta "user_message" pode ser o prompt inicial, a mensagem do usuário, ou a instrução do Assistente de Palco.
    conversation_history: Optional[List[ConversationHistory]] = None # Histórico para contexto
) -> str:
    """
    Obtém uma resposta de IA de um Employee (personagem) específico.
    Constrói o prompt com base no employee_script e no histórico da conversa,
    e delega a chamada HTTP para o connect_ai_service.
    """
    employee = employee_cruds.get_employee_by_name(db, employee_name)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Personagem '{employee_name}' não encontrado.")

    # 1. Construir o prompt completo para a IA
    # Incluir o roteiro do personagem (employee_script) e o histórico da conversa.
    
    # O 'employee_script' deve conter pelo menos uma chave 'context' para o comportamento contínuo
    character_context = employee.employee_script.get("context", "")
    
    # Construir o histórico para o prompt da IA (formato "role-based" ou texto simples)
    history_string = ""
    if conversation_history:
        history_parts = []
        for entry in conversation_history:
            # AQUI: entry.employee_name agora pode ser User.nickname ou o Employee.employee_name
            # Se for o próprio employee_name, podemos rotular como 'AI' ou 'Personagem'
            # para o prompt, ou manter o nome para mais clareza no contexto da IA.
            # Vou usar capitalize para o 'user' e manter o nome do employee para a AI.
            sender_display = entry.employee_name.capitalize() if entry.employee_name == 'user' else employee_name
            history_parts.append(f"{sender_display}: {entry.message_content}")
        history_string = "\n".join(history_parts)
        if history_string:
            history_string = "\n\nHistórico da Conversa:\n" + history_string

    # Montar o prompt final para a IA
    # O prompt deve ser claro e guiar a IA a dar a resposta esperada.
    # Adicionando uma instrução explícita para que a IA gere a "Resposta do Personagem".
    full_prompt = (
        f"{character_context}\n\n"  # Contexto principal do personagem
        f"{history_string}\n\n"     # Histórico da conversa
        f"Usuário: {user_message}\n\n" # A mensagem atual do usuário
        f"Resposta do Personagem:"   # Instrução para a IA responder como o personagem
    ).strip() # Remove espaços em branco extras no início/fim

    logger.debug(f"Prompt final enviado para IA: {full_prompt}")

    # 2. Chamar a API de IA externa via connect_ai_service
    ai_response_text = await connect_ai_service.call_external_ai_api(
        employee.endpoint_url,
        employee.endpoint_key,
        employee.headers_template,
        employee.body_template,
        full_prompt,  # Passa o prompt completo
        employee.ia_name
    )

    return ai_response_text