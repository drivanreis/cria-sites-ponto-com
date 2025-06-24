# File: backend/src/routers/briefing_routers.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from src.db.database import get_db
from src.schemas.briefing_schemas import BriefingCreate, BriefingUpdate, BriefingRead, BriefingWithHistoryRead
from src.schemas.user_schemas import UserRead
from src.cruds import briefing_cruds
from src.services import chat_service, compila_briefing_service
from src.dependencies.oauth_file import get_current_user_from_token
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/briefings",
    tags=["Briefings"],
)

# --- Endpoint para criar um novo Briefing (inicia o processo) ---
@router.post("/", response_model=BriefingRead, status_code=status.HTTP_201_CREATED)
async def create_new_briefing(
    briefing_data: BriefingCreate,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user_from_token)
):
    """
    Cria um novo briefing. Este é o ponto de partida onde o usuário define
    o tema inicial para a entrevista com o Entrevistador Pessoal.
    O status inicial será 'Em Andamento'.
    """
    logger.info(f"Usuário {current_user.id} solicitou a criação de um novo briefing com título: '{briefing_data.title}'")
    
    # Validação para evitar briefings com o mesmo título para o mesmo usuário
    existing_briefing = briefing_cruds.get_briefing_by_user_id_and_title(db, current_user.id, briefing_data.title)
    if existing_briefing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um briefing com este título para o seu usuário. Por favor, escolha um título diferente."
        )

    # Assumimos que na criação inicial, o briefing pode ter content=None
    # E o last_edited_by é o usuário.
    briefing_created = briefing_cruds.create_briefing(
        db=db,
        briefing=briefing_data,
        user_id=current_user.id,
        last_edited_by="user" # O usuário criou o briefing
    )
    if not briefing_created:
        logger.error(f"Falha inesperada ao criar briefing para user_id {current_user.id}.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível criar o briefing."
        )
    return briefing_created

# --- Endpoint para obter briefings de um usuário ---
@router.get("/", response_model=List[BriefingRead])
async def get_briefings_for_user(
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user_from_token),
    skip: int = 0,
    limit: int = 100
):
    """
    Retorna todos os briefings pertencentes ao usuário logado.
    """
    logger.info(f"Usuário {current_user.id} solicitou listagem de briefings.")
    briefings = briefing_cruds.get_briefings_by_user_id(db, user_id=current_user.id, skip=skip, limit=limit)
    return briefings

# --- Endpoint para obter um briefing específico com seu histórico de conversa ---
@router.get("/{briefing_id}", response_model=BriefingWithHistoryRead)
async def get_single_briefing_with_history(
    briefing_id: int,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user_from_token)
):
    """
    Retorna um briefing específico pelo seu ID, incluindo todo o histórico de conversas associado.
    """
    logger.info(f"Usuário {current_user.id} solicitou briefing com ID: {briefing_id} e histórico.")
    briefing = briefing_cruds.get_briefing_with_history(db, briefing_id)
    if not briefing:
        logger.warning(f"Briefing com ID {briefing_id} não encontrado ou não pertence ao usuário {current_user.id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Briefing não encontrado.")
    
    # Garantir que o briefing pertence ao usuário
    if briefing.user_id != current_user.id:
        logger.warning(f"Usuário {current_user.id} tentou acessar briefing {briefing_id} de outro usuário.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para acessar este briefing.")
    
    return briefing

# --- Endpoint para enviar mensagem ao Entrevistador Pessoal e continuar o chat ---
@router.post("/{briefing_id}/chat/{employee_name}", response_model=Dict[str, Any])
async def chat_with_employee(
    briefing_id: int,
    employee_name: str,
    message: Dict[str, str], # Espera um JSON com {"message_content": "sua mensagem aqui"}
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user_from_token)
):
    """
    Envia uma mensagem para um funcionário de IA (e.g., 'Entrevistador Pessoal')
    e recebe a resposta, registrando a conversa.
    Retorna a resposta da IA e um flag se o diálogo terminou.
    """
    user_message_content = message.get("message_content")
    if not user_message_content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Corpo da requisição deve conter 'message_content'.")

    logger.info(f"Usuário {current_user.id} enviou mensagem para briefing {briefing_id} e funcionário {employee_name}.")
    
    chat_response = await chat_service.start_or_continue_chat(
        db=db,
        briefing_id=briefing_id,
        user_message_content=user_message_content,
        employee_name=employee_name,
        user_id=current_user.id
    )
    return chat_response

# --- Endpoint para acionar a compilação do Briefing pelo Assistente de Palco ---
@router.post("/{briefing_id}/compile", response_model=Dict[str, Any])
async def compile_briefing(
    briefing_id: int,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user_from_token)
):
    """
    Aciona o 'Assistente de Palco' para compilar o histórico de conversa
    do briefing em um formato JSON e salvá-lo.
    """
    logger.info(f"Usuário {current_user.id} solicitou compilação para briefing ID: {briefing_id}.")
    
    compilation_result = await compila_briefing_service.compile_briefing_content(
        db=db,
        briefing_id=briefing_id,
        user_id=current_user.id
    )
    return compilation_result

# --- Endpoint para atualizar um Briefing (ex: status, roteiro) ---
@router.put("/{briefing_id}", response_model=BriefingRead)
async def update_existing_briefing(
    briefing_id: int,
    briefing_update: BriefingUpdate,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user_from_token)
):
    """
    Atualiza informações de um briefing existente.
    Pode ser usado para atualizar o 'development_roteiro' ou status.
    """
    logger.info(f"Usuário {current_user.id} solicitou atualização do briefing ID: {briefing_id}.")
    
    db_briefing = briefing_cruds.get_briefing(db, briefing_id)
    if not db_briefing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Briefing não encontrado.")
    
    # Garantir que o briefing pertence ao usuário
    if db_briefing.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para atualizar este briefing.")
    
    # 'last_edited_by' será o usuário para atualizações diretas
    updated_briefing = briefing_cruds.update_briefing(db, db_briefing.id, briefing_update, last_edited_by="user")
    
    if not updated_briefing:
        logger.error(f"Falha inesperada ao atualizar briefing ID {briefing_id}.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Não foi possível atualizar o briefing.")
    
    return updated_briefing

# --- Endpoint para deletar um Briefing ---
@router.delete("/{briefing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_briefing(
    briefing_id: int,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user_from_token)
):
    """
    Deleta um briefing e todo o seu histórico de conversas associado.
    """
    logger.info(f"Usuário {current_user.id} solicitou deleção do briefing ID: {briefing_id}.")
    
    db_briefing = briefing_cruds.get_briefing(db, briefing_id)
    if not db_briefing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Briefing não encontrado.")
    
    # Garantir que o briefing pertence ao usuário
    if db_briefing.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para deletar este briefing.")
    
    if not briefing_cruds.delete_briefing(db, briefing_id):
        logger.error(f"Falha inesperada ao deletar briefing ID {briefing_id}.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Não foi possível deletar o briefing.")
    
    return {"message": "Briefing deletado com sucesso."}