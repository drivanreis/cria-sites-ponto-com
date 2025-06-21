# File: backend/src/services/compila_briefing_service.py

import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.cruds import employee_cruds, briefing_cruds, conversation_history_cruds
from src.schemas.briefing_schemas import BriefingUpdate
from src.services.connect_ai_service import call_external_ai_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def compile_briefing_content(
    db: Session,
    briefing_id: int,
    user_id: int
) -> Dict[str, Any]:
    """
    Compila o briefing via 'Assistente de Palco' e salva no campo 'content' do briefing.
    """
    logger.info(f"Compilando briefing — briefing_id: {briefing_id}, user_id: {user_id}")

    briefing = briefing_cruds.get_briefing(db, briefing_id)
    if not briefing:
        logger.warning(f"Briefing {briefing_id} não encontrado.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Briefing {briefing_id} não encontrado.")

    if briefing.user_id != user_id:
        logger.warning(f"Usuário {user_id} tentou compilar briefing {briefing_id} de outro usuário.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para compilar este briefing.")

    assistant_employee_name = "Assistente de Palco"
    assistant_employee = employee_cruds.get_employee_by_name(db, assistant_employee_name)

    if not assistant_employee:
        logger.error(f"Personagem '{assistant_employee_name}' não encontrado.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Personagem '{assistant_employee_name}' não encontrado.")

    if not isinstance(assistant_employee.employee_script, dict) or 'context' not in assistant_employee.employee_script:
        logger.error(f"Script inválido para '{assistant_employee_name}'.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Script inválido para '{assistant_employee_name}'.")

    # --- Obter histórico completo da conversa ---
    history_entries = conversation_history_cruds.get_conversation_history_by_briefing_id(db, briefing_id, limit=500)

    if not history_entries:
        logger.warning(f"Sem histórico para briefing {briefing_id}. Não é possível compilar.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sem histórico para compilar.")

    formatted_user_prompt = "\n".join(
        f"{entry.sender_type}: {entry.message_content}"
        for entry in history_entries
    )

    system_prompt = f"Contexto do seu papel: {assistant_employee.employee_script['context']}"

    # --- Chamar IA ---
    try:
        raw_ai_response = await call_external_ai_api(
            endpoint_url=assistant_employee.endpoint_url,
            endpoint_key=assistant_employee.endpoint_key,
            headers_template=assistant_employee.headers_template,
            body_template=assistant_employee.body_template,
            system_prompt=system_prompt,
            user_prompt=formatted_user_prompt,
            ia_name=assistant_employee.ia_name
        )
        logger.info(f"Resposta da IA para compilação: {raw_ai_response[:100]}...")

    except Exception as e:
        logger.error(f"Erro ao compilar briefing {briefing_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao compilar briefing: {e}")

    # --- Processar resposta (JSON) ---
    briefing_content_json: Optional[Dict[str, Any]] = None
    try:
        json_start = raw_ai_response.find('{')
        json_end = raw_ai_response.rfind('}')
        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_str = raw_ai_response[json_start:json_end + 1]
            briefing_content_json = json.loads(json_str)
        else:
            briefing_content_json = json.loads(raw_ai_response)

        logger.info(f"Briefing {briefing_id} — JSON decodificado com sucesso.")

    except json.JSONDecodeError as e:
        logger.error(f"Erro de JSON no briefing {briefing_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Resposta da IA não é um JSON válido: {e}")

    except Exception as e:
        logger.error(f"Erro inesperado ao processar resposta da IA — briefing {briefing_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro inesperado na resposta da IA: {e}")

    # --- Salvar briefing ---
    briefing_update = BriefingUpdate(
        content=briefing_content_json,
        status="Compilado"
    )
    updated_briefing = briefing_cruds.update_briefing(db, briefing.id, briefing_update, last_edited_by=assistant_employee_name)

    if not updated_briefing:
        logger.error(f"Falha ao salvar briefing {briefing_id}.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao salvar briefing compilado.")

    logger.info(f"Briefing {briefing_id} compilado e salvo.")

    return {
        "message": "Briefing compilado com sucesso!",
        "briefing_id": briefing_id,
        "content": briefing_content_json
    }
