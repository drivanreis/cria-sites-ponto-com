# File: backend/src/services/character_service.py

from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from fastapi import HTTPException, status

from src.cruds import employee_cruds
from src.models.conversation_history_models import ConversationHistory
from src.services.connect_ai_service import call_external_ai_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_ai_response_for_character(
    db: Session,
    employee_name: str,
    user_message: str,
    conversation_history: Optional[List[ConversationHistory]] = None
) -> str:
    """
    Obtém resposta de IA para um personagem específico.
    Constrói prompt com employee_script e histórico da conversa.
    """
    employee = employee_cruds.get_employee_by_name(db, employee_name)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Personagem '{employee_name}' não encontrado.")

    # Determinar qual campo usar: system_prompt ou context
    system_prompt = ""
    if 'system_prompt' in employee.employee_script:
        system_prompt = employee.employee_script['system_prompt']
    elif 'context' in employee.employee_script:
        system_prompt = employee.employee_script['context']
    else:
        logger.error(f"Script inválido para '{employee_name}'.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Script inválido para '{employee_name}'.")

    # Construir histórico
    formatted_user_prompt = ""
    if conversation_history:
        formatted_user_prompt = "\n".join(
            f"{entry.sender_type}: {entry.message_content}"
            for entry in conversation_history
        )

    # Adicionar mensagem atual do usuário
    formatted_user_prompt += f"\n\nUsuário: {user_message}\n\nResposta do Personagem:"

    logger.debug(f"Prompt final para IA ({employee_name}) — 100: {formatted_user_prompt[:100]}...")

    ai_response_text = await call_external_ai_api(
        endpoint_url=employee.endpoint_url,
        endpoint_key=employee.endpoint_key,
        headers_template=employee.headers_template,
        body_template=employee.body_template,
        system_prompt=system_prompt,
        user_prompt=formatted_user_prompt,
        ia_name=employee.ia_name
    )

    logger.info(f"Resposta da IA ({employee_name}): {ai_response_text[:100]}...")

    return ai_response_text
