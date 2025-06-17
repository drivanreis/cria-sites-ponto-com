# File: backend/src/services/chat_service.py

import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.cruds import employee_cruds, briefing_cruds, conversation_history_cruds, user_cruds # Adicionado user_cruds
from src.schemas.conversation_history_schemas import ConversationHistoryCreate, ConversationHistoryRead
from src.schemas.briefing_schemas import BriefingRead
from src.schemas.employee_schemas import EmployeeRead
from src.services.connect_ai_service import call_external_ai_api # Esta função precisará ser ajustada!

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_or_continue_chat(
    db: Session,
    briefing_id: int,
    user_message_content: str,
    employee_name: str, # Nome do funcionário de IA que irá interagir (e.g., "Entrevistador Pessoal")
    user_id: int # ID do usuário logado
) -> Dict[str, Any]:
    """
    Inicia ou continua um chat com um funcionário de IA específico.
    Registra a mensagem do usuário, chama a IA, registra a resposta da IA.
    Retorna a resposta da IA e um status indicando se o diálogo foi finalizado.
    """
    logger.info(f"Iniciando/continuando chat para briefing_id: {briefing_id} com funcionário: {employee_name} pelo usuário ID: {user_id}")

    # 1. Validar o briefing e o usuário
    briefing = briefing_cruds.get_briefing(db, briefing_id)
    if not briefing:
        logger.warning(f"Briefing com ID {briefing_id} não encontrado.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Briefing com ID {briefing_id} não encontrado."
        )
    if briefing.user_id != user_id:
        logger.warning(f"Usuário {user_id} tentou acessar briefing {briefing_id} de outro usuário.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este briefing."
        )
    
    # Obter o nickname do usuário
    user = user_cruds.get_user(db, user_id)
    if not user:
        logger.error(f"Usuário com ID {user_id} não encontrado.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com ID {user_id} não encontrado."
        )
    user_nickname = user.nickname
    logger.debug(f"Nickname do usuário {user_id}: {user_nickname}")

    # 2. Obter o funcionário de IA
    employee = employee_cruds.get_employee_by_name(db, employee_name)
    if not employee:
        logger.error(f"Funcionário de IA '{employee_name}' não encontrado no banco de dados.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funcionário de IA '{employee_name}' não encontrado."
        )
    
    # Validar que o employee_script possui 'system_prompt'
    if not isinstance(employee.employee_script, dict) or \
       'system_prompt' not in employee.employee_script: # Ajustado para 'system_prompt'
        logger.error(f"employee_script inválido para '{employee_name}': {employee.employee_script}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuração do funcionário de IA '{employee_name}' inválida: 'system_prompt' ausente no employee_script."
        )

    # 3. Registrar a mensagem do usuário no histórico
    user_entry_data = ConversationHistoryCreate(
        briefing_id=briefing_id,
        sender_type=user_nickname, # Ajustado para usar o nickname do usuário
        message_content=user_message_content
    )
    conversation_history_cruds.create_conversation_entry(db, user_entry_data)
    logger.info(f"Mensagem do usuário '{user_nickname}' registrada para briefing {briefing_id}.")

    # 4. Construir o prompt completo para a IA
    # Inclui o system_prompt do funcionário e o histórico da conversa.
    full_conversation_history = conversation_history_cruds.get_conversation_history_by_briefing_id(
        db, briefing_id, limit=50 # Limitar o histórico para não exceder tokens da IA
    )
    
    system_prompt_content = employee.employee_script['system_prompt']
    
    # Formatar o histórico para o prompt da IA.
    # Cada entrada será uma linha "Remetente: Conteúdo da Mensagem".
    # O `call_external_ai_api` será responsável por formatar isso no JSON correto da API.
    formatted_conversation_for_ai = []
    # O 'system_prompt_content' será passado separadamente para call_external_ai_api,
    # que o injetará no lugar certo do body_template.
    
    # Apenas adicione as mensagens da conversa ao histórico para a IA.
    for entry in full_conversation_history:
        # Usamos o sender_type que já pode ser o nickname do usuário ou o nome do funcionário
        formatted_conversation_for_ai.append(f"{entry.sender_type}: {entry.message_content}")
    
    final_user_prompt_for_ai = "\n".join(formatted_conversation_for_ai) # Este é o histórico concatenado para a IA

    # 5. Chamar a API externa da IA
    ai_response_text = await call_external_ai_api(
        endpoint_url=employee.endpoint_url,
        endpoint_key=employee.endpoint_key,
        headers_template=employee.headers_template,
        body_template=employee.body_template,
        system_prompt=system_prompt_content, # Passa o system_prompt separadamente
        user_prompt=final_user_prompt_for_ai, # Passa o histórico da conversa como user_prompt
        ia_name=employee.ia_name
    )
    logger.info(f"Resposta da IA recebida para briefing {briefing_id}: {ai_response_text[:100]}...")

    # 6. Registrar a resposta da IA no histórico
    ai_entry_data = ConversationHistoryCreate(
        briefing_id=briefing_id,
        sender_type=employee_name, # O nome do funcionário como remetente
        message_content=ai_response_text
    )
    conversation_history_cruds.create_conversation_entry(db, ai_entry_data)
    logger.info(f"Resposta da IA registrada para briefing {briefing_id}.")

    # 7. Verificar se o diálogo foi finalizado
    dialog_finished = "FINALIZAR API" in ai_response_text.upper() # Usar .upper() para case-insensitivity
    
    # Opcional: Remover "FINALIZAR API" da resposta final para o usuário
    if dialog_finished:
        ai_response_text = ai_response_text.replace("FINALIZAR API", "").strip()
        logger.info(f"Diálogo com IA finalizado para briefing {briefing_id}.")

    return {
        "ai_response": ai_response_text,
        "dialog_finished": dialog_finished
    }