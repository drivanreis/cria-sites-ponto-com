# backend/src/routers/auth_user_routers.py

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.user_models import User
from src.core.security import create_access_token, verify_password
from src.schemas.token_schemas import Token
from datetime import datetime

router = APIRouter(prefix="/auth/login", tags=["User Auth"])

@router.post("/user", response_model=Token)
def login_common_user(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas para usuário.")

    token_data = {
        "id": user.id,
        "username": user.nickname,
        "email": user.email,
        "user_type": "user"
    }

    user.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.commit()

    token = create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer"}
