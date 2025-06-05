import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.cruds import employee_cruds, briefing_cruds, conversation_history_cruds
from src.schemas.conversation_history_schemas import ConversationHistoryCreate, ConversationHistoryRead
from src.schemas.briefing_schemas import BriefingRead
from src.schemas.employee_schemas import EmployeeRead
from src.services.connect_ai_service import call_external_ai_api

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
    logger.info(f"Iniciando/continuando chat para briefing_id: {briefing_id} com funcionário: {employee_name}")

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

    # 2. Obter o funcionário de IA
    employee = employee_cruds.get_employee_by_name(db, employee_name)
    if not employee:
        logger.error(f"Funcionário de IA '{employee_name}' não encontrado no banco de dados.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funcionário de IA '{employee_name}' não encontrado."
        )
    
    # Validar que o employee_script possui 'intro' e 'context'
    if not isinstance(employee.employee_script, dict) or \
       'intro' not in employee.employee_script or \
       'context' not in employee.employee_script:
        logger.error(f"employee_script inválido para '{employee_name}': {employee.employee_script}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuração do funcionário de IA '{employee_name}' inválida: employee_script incompleto."
        )

    # 3. Registrar a mensagem do usuário no histórico
    user_entry_data = ConversationHistoryCreate(
        briefing_id=briefing_id,
        sender_type="user",
        message_content=user_message_content
    )
    conversation_history_cruds.create_conversation_entry(db, user_entry_data)
    logger.info(f"Mensagem do usuário registrada para briefing {briefing_id}.")

    # 4. Construir o prompt completo para a IA
    # Inclui o contexto, a introdução (se for a primeira mensagem lógica), e o histórico da conversa.
    full_conversation_history = conversation_history_cruds.get_conversation_history_by_briefing_id(
        db, briefing_id, limit=50 # Limitar o histórico para não exceder tokens da IA
    )
    
    # Formatar o histórico para o prompt da IA
    # A IA precisa ver o contexto e as interações passadas para manter a coerência.
    # O formato pode variar dependendo da IA (e.g., [{'role': 'user', 'content': '...'}] para OpenAI-like)
    
    # Para o Gemini e OpenAI-like, o 'context' e 'intro' podem ser parte do prompt inicial
    # ou de uma "mensagem de sistema". Adaptamos isso para 'user_input' em call_external_ai_api.
    
    # Construir o histórico para a IA
    formatted_history = []
    # Adiciona o contexto do funcionário como a primeira parte do prompt
    # Isso será o 'System Prompt' ou parte do 'User' prompt inicial
    formatted_history.append(f"Contexto do seu papel: {employee.employee_script['context']}")
    
    # Adicionar o histórico de conversas como string formatada
    for entry in full_conversation_history:
        formatted_history.append(f"{entry.sender_type}: {entry.message_content}")
    
    # A última mensagem do usuário (current_user_message) já foi adicionada ao histórico
    # e, portanto, já está em `formatted_history`.

    # Juntar tudo para o prompt final da IA
    # O `call_external_ai_api` espera um único `prompt_content` que ele injetará no body_template.
    # Então, concatenamos todo o histórico aqui.
    final_prompt_for_ai = "\n".join(formatted_history)
    
    # Opcional: Adicionar a intro apenas uma vez no início da conversa se necessário
    # Isso pode ser gerenciado de forma mais sofisticada se houver um controle de "primeira interação"
    # No momento, o `context` já deve guiar a IA. A `intro` é mais para o frontend mostrar.
    # Se a IA precisa da `intro` para seu comportamento, ela deveria estar no `context`.

    # 5. Chamar a API externa da IA
    ai_response_text = await call_external_ai_api(
        endpoint_url=employee.endpoint_url,
        endpoint_key=employee.endpoint_key,
        headers_template=employee.headers_template,
        body_template=employee.body_template,
        prompt_content=final_prompt_for_ai, # O prompt_content já inclui o contexto e o histórico
        ia_name=employee.ia_name
    )
    logger.info(f"Resposta da IA recebida para briefing {briefing_id}: {ai_response_text[:50]}...")

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