# File: backend/src/services/chat_service.py

import json
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.cruds import employee_cruds, briefing_cruds, conversation_history_cruds, user_cruds
from src.schemas.conversation_history_schemas import ConversationHistoryCreate
from src.services.connect_ai_service import call_external_ai_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_or_continue_chat(
    db: Session,
    briefing_id: int,
    user_message_content: str,
    employee_name: str,
    user_id: int
) -> Dict[str, Any]:
    """
    Inicia ou continua um chat com um personagem de IA.
    Registra a mensagem do usuário e a resposta da IA.
    """
    logger.info(f"Iniciando/continuando chat — briefing_id: {briefing_id}, IA: {employee_name}, user_id: {user_id}")

    briefing = briefing_cruds.get_briefing(db, briefing_id)
    if not briefing:
        logger.warning(f"Briefing {briefing_id} não encontrado.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Briefing {briefing_id} não encontrado.")

    if briefing.user_id != user_id:
        logger.warning(f"Usuário {user_id} tentou acessar briefing {briefing_id} de outro usuário.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para este briefing.")

    user = user_cruds.get_user(db, user_id)
    if not user:
        logger.error(f"Usuário {user_id} não encontrado.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Usuário {user_id} não encontrado.")

    user_nickname = user.nickname

    employee = employee_cruds.get_employee_by_name(db, employee_name)
    if not employee:
        logger.error(f"Personagem de IA '{employee_name}' não encontrado.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Personagem de IA '{employee_name}' não encontrado.")

    if not isinstance(employee.employee_script, dict) or 'system_prompt' not in employee.employee_script:
        logger.error(f"Script inválido para '{employee_name}'.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Script inválido para '{employee_name}'.")

    # --- Registrar mensagem do usuário ---
    user_entry = ConversationHistoryCreate(
        briefing_id=briefing_id,
        sender_type=user_nickname,
        message_content=user_message_content
    )
    conversation_history_cruds.create_conversation_entry(db, user_entry)
    logger.info(f"Mensagem do usuário '{user_nickname}' registrada no briefing {briefing_id}.")

    # --- Obter histórico para enviar para a IA ---
    history_entries = conversation_history_cruds.get_conversation_history_by_briefing_id(db, briefing_id, limit=50)

    formatted_user_prompt = "\n".join(
        f"{entry.sender_type}: {entry.message_content}"
        for entry in history_entries
    )

    # --- Chamar API de IA ---
    ai_response_text = await call_external_ai_api(
        endpoint_url=employee.endpoint_url,
        endpoint_key=employee.endpoint_key,
        headers_template=employee.headers_template,
        body_template=employee.body_template,
        system_prompt=employee.employee_script['system_prompt'],
        user_prompt=formatted_user_prompt,
        ia_name=employee.ia_name
    )

    logger.info(f"Resposta da IA para briefing {briefing_id}: {ai_response_text[:100]}...")

    # --- Registrar resposta da IA ---
    ai_entry = ConversationHistoryCreate(
        briefing_id=briefing_id,
        sender_type=employee_name,
        message_content=ai_response_text
    )
    conversation_history_cruds.create_conversation_entry(db, ai_entry)
    logger.info(f"Resposta da IA registrada no briefing {briefing_id}.")

    # --- Checar se o diálogo foi finalizado ---
    dialog_finished = "FINALIZAR API" in ai_response_text.upper()

    if dialog_finished:
        ai_response_text = ai_response_text.replace("FINALIZAR API", "").strip()
        logger.info(f"Diálogo finalizado para briefing {briefing_id}.")

    return {
        "ai_response": ai_response_text,
        "dialog_finished": dialog_finished
    }
