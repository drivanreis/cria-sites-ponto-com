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
    user_id: int # Para validação de propriedade do briefing
) -> Dict[str, Any]:
    """
    Aciona o 'Assistente de Palco' para compilar o histórico de conversa
    em um formato JSON e salva no campo 'content' do briefing.
    As instruções para a IA são extraídas do employee_script do Assistente de Palco.
    """
    logger.info(f"Iniciando compilação de briefing para ID: {briefing_id} por user_id: {user_id}")

    # 1. Validar e obter o briefing
    briefing = briefing_cruds.get_briefing(db, briefing_id)
    if not briefing:
        logger.warning(f"Briefing com ID {briefing_id} não encontrado para compilação.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Briefing com ID {briefing_id} não encontrado."
        )
    if briefing.user_id != user_id:
        logger.warning(f"Usuário {user_id} tentou compilar briefing {briefing_id} de outro usuário.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para compilar este briefing."
        )

    # 2. Obter o funcionário 'Assistente de Palco'
    assistant_employee_name = "Assistente de Palco"
    assistant_employee = employee_cruds.get_employee_by_name(db, assistant_employee_name)

    if not assistant_employee:
        logger.error(f"Funcionário de IA '{assistant_employee_name}' não encontrado para compilação.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Funcionário de IA '{assistant_employee_name}' (Assistente de Palco) não configurado no sistema."
        )

    # Validar que o employee_script possui 'context'
    if not isinstance(assistant_employee.employee_script, dict) or \
       'context' not in assistant_employee.employee_script:
        logger.error(f"employee_script inválido para '{assistant_employee_name}': {assistant_employee.employee_script}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuração do funcionário de IA '{assistant_employee_name}' inválida: employee_script sem 'context'."
        )

    # 3. Recuperar todo o histórico de conversas do briefing
    full_conversation_history = conversation_history_cruds.get_conversation_history_by_briefing_id(
        db, briefing_id=briefing_id, limit=500 # Aumentar o limite para compilação completa
    )

    if not full_conversation_history:
        logger.warning(f"Nenhum histórico de conversa encontrado para briefing_id: {briefing_id}. Não é possível compilar.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum histórico de conversa para compilar neste briefing."
        )

    # 4. Construir o prompt completo para o 'Assistente de Palco'
    # O prompt agora usa o 'context' do employee_script para as instruções principais da IA.
    compilation_prompt_parts = [f"Contexto do seu papel: {assistant_employee.employee_script['context']}"]

    compilation_prompt_parts.append("\n--- Histórico da Conversa para Compilação ---")
    for entry in full_conversation_history:
        compilation_prompt_parts.append(f"{entry.sender_type}: {entry.message_content}")
    compilation_prompt_parts.append("--- Fim do Histórico ---")

    final_compilation_prompt = "\n".join(compilation_prompt_parts)

    # 5. Chamar a API externa da IA para compilação
    try:
        raw_ai_response = await call_external_ai_api(
            endpoint_url=assistant_employee.endpoint_url,
            endpoint_key=assistant_employee.endpoint_key,
            headers_template=assistant_employee.headers_template,
            body_template=assistant_employee.body_template,
            prompt_content=final_compilation_prompt,
            ia_name=assistant_employee.ia_name
        )
        logger.info(f"Resposta bruta da IA para compilação recebida: {raw_ai_response[:100]}...")
    except Exception as e:
        logger.error(f"Erro ao chamar a IA para compilação do briefing {briefing_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor ao compilar o briefing: {e}"
        )

    # 6. Processar e validar a resposta JSON da IA
    briefing_content_json: Optional[Dict[str, Any]] = None
    try:
        # Tentar extrair apenas o JSON se a IA incluir texto extra ou Markdown
        json_start = raw_ai_response.find('{')
        json_end = raw_ai_response.rfind('}')
        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_str = raw_ai_response[json_start : json_end + 1]
            briefing_content_json = json.loads(json_str)
        else:
            # Se não encontrar chaves de JSON, tentar parsear a resposta inteira
            briefing_content_json = json.loads(raw_ai_response)

        logger.info(f"Briefing content JSON parsado com sucesso para briefing {briefing_id}.")
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON da resposta da IA para briefing {briefing_id}: {e} - Resposta: {raw_ai_response}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"A IA não retornou um formato JSON válido para o briefing. Erro: {e}"
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao processar resposta JSON da IA para briefing {briefing_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado ao processar a resposta da IA para o briefing: {e}"
        )

    # 7. Salvar o conteúdo compilado no briefing
    briefing_update_data = BriefingUpdate(
        content=briefing_content_json,
        status="Compilado" # Atualiza o status do briefing
    )
    # Note: briefing_cruds.update_briefing espera briefing_id como primeiro argumento após db.
    updated_briefing = briefing_cruds.update_briefing(db, briefing.id, briefing_update_data, last_edited_by=assistant_employee_name)

    if not updated_briefing:
        logger.error(f"Falha ao atualizar briefing {briefing_id} com conteúdo compilado.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar o briefing compilado."
        )

    logger.info(f"Briefing ID {briefing_id} compilado e salvo com sucesso.")
    return {"message": "Briefing compilado com sucesso!", "briefing_id": briefing_id, "content": briefing_content_json}