from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.user_models import User
from src.schemas.token_schemas import Token
from src.core.security import create_access_token
from datetime import datetime

router = APIRouter(prefix="/auth/social", tags=["Social Auth"])

# Simulando retorno do Google/GitHub com identificadores únicos
@router.post("/google", response_model=Token)
def login_google(google_id: str, nickname: str, email: str, db: Session = Depends(get_db)):
    if not google_id or not email:
        raise HTTPException(status_code=400, detail="Dados do Google incompletos")

    user = db.query(User).filter(User.google_id == google_id).first()

    if not user:
        # Usuário novo via Google
        user = User(
            google_id=google_id,
            nickname=nickname,
            email=email,
            email_verified=True,
            status="Ativo",
            creation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.add(user)
        db.commit()
        db.refresh(user)

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


@router.post("/github", response_model=Token)
def login_github(github_id: str, nickname: str, db: Session = Depends(get_db)):
    if not github_id:
        raise HTTPException(status_code=400, detail="ID do GitHub não informado")

    user = db.query(User).filter(User.github_id == github_id).first()

    if not user:
        # Usuário novo via GitHub
        user = User(
            github_id=github_id,
            nickname=nickname,
            status="Ativo",
            creation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.add(user)
        db.commit()
        db.refresh(user)

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
