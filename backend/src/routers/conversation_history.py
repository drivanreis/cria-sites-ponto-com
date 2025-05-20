# File: backend/src/routers/conversation_history.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.cruds import conversation_history as crud_conv_history
from src.schemas.conversation_history import ConversationHistoryCreate, ConversationHistoryUpdate, ConversationHistoryInDB
from src.db.database import get_db

router = APIRouter()

@router.post("/", response_model=ConversationHistoryInDB, status_code=status.HTTP_201_CREATED)
def create_new_conversation_message(
    message: ConversationHistoryCreate,
    db: Session = Depends(get_db)
):
    # Check if briefing_id exists (optional, but good for data integrity)
    # from src.cruds.briefing import get_briefing # Avoid circular import if possible, or pass dependency
    # if not get_briefing(db, message.briefing_id):
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Briefing not found for this message")
    
    return crud_conv_history.create_conversation_message(db=db, message=message)

@router.get("/", response_model=List[ConversationHistoryInDB])
def read_conversation_history(
    briefing_id: int, # Briefing ID is mandatory for retrieving conversation history
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    history = crud_conv_history.get_conversation_history_by_briefing(db, briefing_id=briefing_id, skip=skip, limit=limit)
    if not history:
        # It's okay if history is empty, but if briefing_id itself is invalid, maybe raise 404
        # For now, just return empty list if no messages
        pass
    return history

@router.get("/{message_id}", response_model=ConversationHistoryInDB)
def read_conversation_message(message_id: int, db: Session = Depends(get_db)):
    db_message = crud_conv_history.get_conversation_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation message not found")
    return db_message

@router.put("/{message_id}", response_model=ConversationHistoryInDB)
def update_existing_conversation_message(
    message_id: int,
    message: ConversationHistoryUpdate,
    db: Session = Depends(get_db)
):
    db_message = crud_conv_history.update_conversation_message(db, message_id=message_id, message=message)
    if db_message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation message not found")
    return db_message

@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_conversation_message(message_id: int, db: Session = Depends(get_db)):
    success = crud_conv_history.delete_conversation_message(db, message_id=message_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation message not found")
    return {"message": "Conversation message deleted successfully"}