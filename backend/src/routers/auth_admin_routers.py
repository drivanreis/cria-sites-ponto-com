# backend/src/routers/aute_admin_routers.py

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.admin_user_models import AdminUser
from src.core.security import create_access_token, verify_password
from src.schemas.token_schemas import Token
from datetime import datetime

router = APIRouter(prefix="/auth/login", tags=["Admin Auth"])

@router.post("/admin", response_model=Token)
def login_admin_user(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not admin or not verify_password(password, admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas para admin.")

    token_data = {
        "id": admin.id,
        "username": admin.username,
        "user_type": "admin"
    }
    token = create_access_token(token_data)

    admin.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.commit()

    return {"access_token": token, "token_type": "bearer"}
