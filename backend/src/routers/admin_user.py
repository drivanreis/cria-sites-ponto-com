# File: backend/src/routers/admin_user.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.cruds import admin_user as crud_admin_user
from src.schemas.admin_user import AdminUserCreate, AdminUserUpdate, AdminUserInDB
from src.db.database import get_db

router = APIRouter()

@router.post("/", response_model=AdminUserInDB, status_code=status.HTTP_201_CREATED)
def create_new_admin_user(admin_user: AdminUserCreate, db: Session = Depends(get_db)):
    db_admin_user = crud_admin_user.get_admin_user_by_email(db, email=admin_user.email)
    if db_admin_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Admin user email already registered")
    return crud_admin_user.create_admin_user(db=db, admin_user=admin_user)

@router.get("/", response_model=List[AdminUserInDB])
def read_admin_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    admin_users = crud_admin_user.get_admin_users(db, skip=skip, limit=limit)
    return admin_users

@router.get("/{admin_user_id}", response_model=AdminUserInDB)
def read_admin_user(admin_user_id: int, db: Session = Depends(get_db)):
    db_admin_user = crud_admin_user.get_admin_user(db, admin_user_id=admin_user_id)
    if db_admin_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found")
    return db_admin_user

@router.put("/{admin_user_id}", response_model=AdminUserInDB)
def update_existing_admin_user(admin_user_id: int, admin_user: AdminUserUpdate, db: Session = Depends(get_db)):
    db_admin_user = crud_admin_user.update_admin_user(db, admin_user_id=admin_user_id, admin_user=admin_user)
    if db_admin_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found")
    return db_admin_user

@router.delete("/{admin_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_admin_user(admin_user_id: int, db: Session = Depends(get_db)):
    success = crud_admin_user.delete_admin_user(db, admin_user_id=admin_user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found")
    return {"message": "Admin user deleted successfully"}