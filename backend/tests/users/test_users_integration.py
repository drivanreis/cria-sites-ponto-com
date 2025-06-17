# File: backend/tests/users/test_users_integration.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status

# Importe o seu app FastAPI
from src.main import app 

# Importe os schemas, models e cruds necessários
from src.schemas.user_schemas import UserCreate, UserUpdate
from src.models.user_models import User
from src.cruds import user_cruds
from src.core.security import get_password_hash # Para criar usuários diretamente no DB se necessário

# Importe as fixtures do seu conftest.py
# Estas fixtures são cruciais para configurar o ambiente de teste
# Certifique-se de que seu conftest.py as forneça:
# - db_session_override: Uma sessão de banco de dados limpa para cada teste
# - client: Uma instância do TestClient do FastAPI para sua aplicação
# - create_test_user: Uma função auxiliar para criar usuários no banco de dados para os testes
# - get_user_token: Uma função auxiliar para obter um token JWT para um usuário
from tests.conftest import db_session_override, client, create_test_user, get_user_token, get_admin_token

# Helper para gerar dados de usuário válidos para testes
def get_valid_user_data(suffix: str = "") -> dict:
    """Gera dados de usuário válidos e únicos para requisições."""
    return {
        "name": f"Integration User {suffix}",
        "email": f"integration.user.{suffix}@example.com",
        "phone_number": f"55119{suffix.zfill(7)}", # Garante unicidade e formato
        "password": "SecurePassword123!"
    }

def get_valid_admin_data(suffix: str = "") -> dict:
    """Gera dados de admin válidos e únicos para requisições."""
    return {
        "name": f"Integration Admin {suffix}",
        "email": f"integration.admin.{suffix}@example.com",
        "phone_number": f"55118{suffix.zfill(7)}", # Garante unicidade e formato
        "password": "AdminSecurePassword123!",
        "is_admin": True # Importante para admins
    }

# --- Testes de Integração para Endpoints de Usuário ---

# Testes de Criação de Usuário (POST /users/)
def test_create_user_success(client: TestClient, db_session_override: Session):
    user_data = get_valid_user_data("create_success")
    response = client.post("/users/", json=user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert "password_hash" not in data # A senha hashed não deve ser retornada
    assert data["id"] is not None
    assert data["is_admin"] is False # Deve ser False por padrão
    assert data["email_verified"] is False
    assert data["status"] == "active"

    # Verifique se o usuário existe no banco de dados
    db_user = db_session_override.query(User).filter(User.email == user_data["email"]).first()
    assert db_user is not None
    assert user_cruds.verify_user_password(db_session_override, db_user.id, user_data["password"])


def test_create_user_duplicate_email(client: TestClient, db_session_override: Session):
    user_data = get_valid_user_data("duplicate_email_api")
    client.post("/users/", json=user_data) # Cria o primeiro usuário
    
    # Tenta criar outro com o mesmo email
    duplicate_user_data = get_valid_user_data("duplicate_email_api_other")
    duplicate_user_data["email"] = user_data["email"] # Mesma email
    
    response = client.post("/users/", json=duplicate_user_data)
    
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "Email já registrado por outro usuário." in response.json()["detail"]


def test_create_user_duplicate_phone_number(client: TestClient, db_session_override: Session):
    user_data = get_valid_user_data("duplicate_phone_api")
    client.post("/users/", json=user_data) # Cria o primeiro usuário
    
    # Tenta criar outro com o mesmo phone_number
    duplicate_user_data = get_valid_user_data("duplicate_phone_api_other")
    duplicate_user_data["phone_number"] = user_data["phone_number"] # Mesmo phone_number
    
    response = client.post("/users/", json=duplicate_user_data)
    
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "Número de telefone já registrado por outro usuário." in response.json()["detail"]

@pytest.mark.parametrize("field", ["name", "email", "password", "phone_number"])
def test_create_user_missing_required_fields(client: TestClient, db_session_override: Session, field: str):
    user_data = get_valid_user_data(f"missing_{field}")
    del user_data[field] # Remove o campo necessário
    
    response = client.post("/users/", json=user_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY # Erro de validação Pydantic
    assert field in response.json()["detail"][0]["loc"] # Verifica se o campo ausente é reportado

def test_create_user_invalid_email_format(client: TestClient, db_session_override: Session):
    user_data = get_valid_user_data("invalid_email")
    user_data["email"] = "invalid-email" # Email inválido
    
    response = client.post("/users/", json=user_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "email" in response.json()["detail"][0]["loc"]

def test_create_user_weak_password(client: TestClient, db_session_override: Session):
    user_data = get_valid_user_data("weak_password")
    user_data["password"] = "short" # Senha fraca
    
    response = client.post("/users/", json=user_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "password" in response.json()["detail"][0]["loc"]
    assert "String should have at least 8 characters" in response.json()["detail"][0]["msg"]

# Testes de Leitura de Usuário (GET /users/{user_id}, GET /users/me, GET /users/)
def test_read_own_user_profile_via_me(client: TestClient, db_session_override: Session):
    user_password = "SelfReadP@ss1!"
    user_credentials = create_test_user(
        db_session_override, 
        "Self Read User", 
        "self_read_profile_me@example.com", 
        user_password, 
        phone_number="5511987650001"
    )
    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)
    
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/users/me", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user_credentials.id
    assert data["email"] == user_credentials.email
    assert "password_hash" not in data


def test_read_user_as_admin(client: TestClient, db_session_override: Session):
    admin_data = get_valid_admin_data("read_admin")
    admin_user = create_test_user(
        db_session_override, 
        admin_data["name"], 
        admin_data["email"], 
        admin_data["password"], 
        phone_number=admin_data["phone_number"], 
        is_admin=True
    )
    admin_token = get_admin_token(client, db_session_override, admin_user.email, admin_data["password"])

    user_to_read_data = get_valid_user_data("read_by_admin")
    user_to_read = create_test_user(
        db_session_override, 
        user_to_read_data["name"], 
        user_to_read_data["email"], 
        user_to_read_data["password"], 
        phone_number=user_to_read_data["phone_number"]
    )
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"/users/{user_to_read.id}", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user_to_read.id
    assert data["email"] == user_to_read.email

def test_read_other_user_as_normal_user_forbidden(client: TestClient, db_session_override: Session):
    user1_password = "User1P@ss1!"
    user1 = create_test_user(
        db_session_override, 
        "User One", 
        "user1_read_forbidden@example.com", 
        user1_password, 
        phone_number="5511987650002"
    )
    user1_token = get_user_token(client, db_session_override, user1.email, user1_password)

    user2 = create_test_user(
        db_session_override, 
        "User Two", 
        "user2_read_forbidden@example.com", 
        "User2P@ss1!", 
        phone_number="5511987650003"
    )
    
    headers = {"Authorization": f"Bearer {user1_token}"}
    response = client.get(f"/users/{user2.id}", headers=headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN # Ou 404 dependendo da sua lógica de segurança
    assert "Você não tem permissão para acessar este recurso." in response.json()["detail"]


def test_read_all_users_as_admin(client: TestClient, db_session_override: Session):
    admin_data = get_valid_admin_data("read_all_admin")
    admin_user = create_test_user(
        db_session_override, 
        admin_data["name"], 
        admin_data["email"], 
        admin_data["password"], 
        phone_number=admin_data["phone_number"], 
        is_admin=True
    )
    admin_token = get_admin_token(client, db_session_override, admin_user.email, admin_data["password"])

    # Crie alguns usuários
    create_test_user(db_session_override, "User A", "user_a@example.com", "PassA123!", phone_number="5511987650004")
    create_test_user(db_session_override, "User B", "user_b@example.com", "PassB123!", phone_number="5511987650005")

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/users/", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # Deve haver pelo menos o admin e os 2 usuários criados (total de 3)
    # A quantidade exata pode variar dependendo da fixture de limpeza, então >= 3 é seguro.
    assert len(data) >= 3 


def test_read_all_users_as_normal_user_forbidden(client: TestClient, db_session_override: Session):
    user_password = "NormalUserP@ss1!"
    normal_user = create_test_user(
        db_session_override, 
        "Normal User", 
        "normal_user_read_all@example.com", 
        user_password, 
        phone_number="5511987650006"
    )
    normal_user_token = get_user_token(client, db_session_override, normal_user.email, user_password)
    
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    response = client.get("/users/", headers=headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN # Ou 404 dependendo da sua lógica de segurança
    assert "Você não tem permissão para acessar este recurso." in response.json()["detail"]

def test_read_non_existent_user_as_admin(client: TestClient, db_session_override: Session):
    admin_data = get_valid_admin_data("read_nonexistent_admin")
    admin_user = create_test_user(
        db_session_override, 
        admin_data["name"], 
        admin_data["email"], 
        admin_data["password"], 
        phone_number=admin_data["phone_number"], 
        is_admin=True
    )
    admin_token = get_admin_token(client, db_session_override, admin_user.email, admin_data["password"])
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/users/999999", headers=headers) # ID que não existe
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Usuário não encontrado" in response.json()["detail"]


# Testes de Atualização de Usuário (PUT/PATCH /users/{user_id}, PATCH /users/me)
def test_update_own_user_profile_via_me(client: TestClient, db_session_override: Session):
    user_password = "SelfUpdateP@ss1!"
    user_credentials = create_test_user(
        db_session_override, 
        "Self Update User", 
        "self_update_me_api@example.com", 
        user_password, 
        phone_number="5511987650007"
    )
    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)
    
    headers = {"Authorization": f"Bearer {user_token}"}
    updated_data = {"name": "Updated Self Name Via Me", "phone_number": "5511987650008"}
    
    response = client.patch("/users/me", headers=headers, json=updated_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == updated_data["name"]
    assert data["phone_number"] == updated_data["phone_number"]
    
    # Verifique no banco de dados
    db_user = db_session_override.query(User).filter(User.id == user_credentials.id).first()
    assert db_user.name == updated_data["name"]
    assert db_user.phone_number == updated_data["phone_number"]

def test_update_own_user_password_via_me(client: TestClient, db_session_override: Session):
    user_password = "OldPass123!"
    new_password = "NewPass456!"
    user_credentials = create_test_user(
        db_session_override, 
        "Password Changer", 
        "pass_changer@example.com", 
        user_password, 
        phone_number="5511987650009"
    )
    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)
    
    headers = {"Authorization": f"Bearer {user_token}"}
    updated_data = {"password": new_password}
    
    response = client.patch("/users/me", headers=headers, json=updated_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "password_hash" not in data # Não deve retornar o hash
    
    # Tente logar com a nova senha para verificar
    login_response = client.post(
        "/auth/login",
        data={"username": user_credentials.email, "password": new_password}
    )
    assert login_response.status_code == status.HTTP_200_OK

def test_update_user_as_admin(client: TestClient, db_session_override: Session):
    admin_data = get_valid_admin_data("update_admin")
    admin_user = create_test_user(
        db_session_override, 
        admin_data["name"], 
        admin_data["email"], 
        admin_data["password"], 
        phone_number=admin_data["phone_number"], 
        is_admin=True
    )
    admin_token = get_admin_token(client, db_session_override, admin_user.email, admin_data["password"])

    user_to_update_data = get_valid_user_data("update_by_admin")
    user_to_update = create_test_user(
        db_session_override, 
        user_to_update_data["name"], 
        user_to_update_data["email"], 
        user_to_update_data["password"], 
        phone_number=user_to_update_data["phone_number"]
    )
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    updated_data = {"name": "Updated By Admin", "status": "blocked", "is_admin": True} # Alterar status e tornar admin
    
    response = client.patch(f"/users/{user_to_update.id}", headers=headers, json=updated_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user_to_update.id
    assert data["name"] == updated_data["name"]
    assert data["status"] == updated_data["status"]
    assert data["is_admin"] is True # Admin pode alterar is_admin

    # Verifique no banco de dados
    db_user = db_session_override.query(User).filter(User.id == user_to_update.id).first()
    assert db_user.name == updated_data["name"]
    assert db_user.status == updated_data["status"]
    assert db_user.is_admin is True


def test_update_other_user_as_normal_user_forbidden(client: TestClient, db_session_override: Session):
    user1_password = "User1UpdateForbiddenP@ss1!"
    user1 = create_test_user(
        db_session_override, 
        "User One Update", 
        "user1_update_forbidden@example.com", 
        user1_password, 
        phone_number="5511987650010"
    )
    user1_token = get_user_token(client, db_session_override, user1.email, user1_password)

    user2 = create_test_user(
        db_session_override, 
        "User Two Update", 
        "user2_update_forbidden@example.com", 
        "User2UpdateP@ss1!", 
        phone_number="5511987650011"
    )
    
    headers = {"Authorization": f"Bearer {user1_token}"}
    updated_data = {"name": "Attempted Update"}
    
    response = client.patch(f"/users/{user2.id}", headers=headers, json=updated_data)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN # Ou 404 dependendo da sua lógica de segurança
    assert "Você não tem permissão para acessar este recurso." in response.json()["detail"]


def test_update_user_invalid_data(client: TestClient, db_session_override: Session):
    admin_data = get_valid_admin_data("update_invalid_data")
    admin_user = create_test_user(
        db_session_override, 
        admin_data["name"], 
        admin_data["email"], 
        admin_data["password"], 
        phone_number=admin_data["phone_number"], 
        is_admin=True
    )
    admin_token = get_admin_token(client, db_session_override, admin_user.email, admin_data["password"])

    user_to_update_data = get_valid_user_data("update_invalid_user")
    user_to_update = create_test_user(
        db_session_override, 
        user_to_update_data["name"], 
        user_to_update_data["email"], 
        user_to_update_data["password"], 
        phone_number=user_to_update_data["phone_number"]
    )
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    invalid_data = {"email": "invalid-email-format"} # Email inválido
    
    response = client.patch(f"/users/{user_to_update.id}", headers=headers, json=invalid_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "email" in response.json()["detail"][0]["loc"]


# Testes de Deleção de Usuário (DELETE /users/{user_id})
def test_delete_user_as_admin(client: TestClient, db_session_override: Session):
    admin_data = get_valid_admin_data("delete_admin")
    admin_user = create_test_user(
        db_session_override, 
        admin_data["name"], 
        admin_data["email"], 
        admin_data["password"], 
        phone_number=admin_data["phone_number"], 
        is_admin=True
    )
    admin_token = get_admin_token(client, db_session_override, admin_user.email, admin_data["password"])

    user_to_delete_data = get_valid_user_data("delete_by_admin")
    user_to_delete = create_test_user(
        db_session_override, 
        user_to_delete_data["name"], 
        user_to_delete_data["email"], 
        user_to_delete_data["password"], 
        phone_number=user_to_delete_data["phone_number"]
    )
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(f"/users/{user_to_delete.id}", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Usuário deletado com sucesso"
    
    # Verifique se o usuário foi realmente deletado do banco de dados
    db_user = db_session_override.query(User).filter(User.id == user_to_delete.id).first()
    assert db_user is None


def test_delete_user_as_self_forbidden(client: TestClient, db_session_override: Session):
    user_password = "SelfDeleteForbiddenP@ss1!"
    user_credentials = create_test_user(
        db_session_override, 
        "Self Delete User", 
        "self_delete_forbidden@example.com", 
        user_password, 
        phone_number="5511987650012"
    )
    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)
    
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.delete(f"/users/{user_credentials.id}", headers=headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN # Usuários não devem poder se auto-deletar (pelo ID)
    assert "Você não tem permissão para acessar este recurso." in response.json()["detail"]


def test_delete_other_user_as_normal_user_forbidden(client: TestClient, db_session_override: Session):
    user1_password = "User1DeleteForbiddenP@ss1!"
    user1 = create_test_user(
        db_session_override, 
        "User One Delete", 
        "user1_delete_forbidden@example.com", 
        user1_password, 
        phone_number="5511987650013"
    )
    user1_token = get_user_token(client, db_session_override, user1.email, user1_password)

    user2 = create_test_user(
        db_session_override, 
        "User Two Delete", 
        "user2_delete_forbidden@example.com", 
        "User2DeleteP@ss1!", 
        phone_number="5511987650014"
    )
    
    headers = {"Authorization": f"Bearer {user1_token}"}
    response = client.delete(f"/users/{user2.id}", headers=headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN # Ou 404 dependendo da sua lógica de segurança
    assert "Você não tem permissão para acessar este recurso." in response.json()["detail"]

def test_delete_non_existent_user_as_admin(client: TestClient, db_session_override: Session):
    admin_data = get_valid_admin_data("delete_nonexistent_admin")
    admin_user = create_test_user(
        db_session_override, 
        admin_data["name"], 
        admin_data["email"], 
        admin_data["password"], 
        phone_number=admin_data["phone_number"], 
        is_admin=True
    )
    admin_token = get_admin_token(client, db_session_override, admin_user.email, admin_data["password"])
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete("/users/999999", headers=headers) # ID que não existe
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Usuário não encontrado" in response.json()["detail"]

# Testes de Autenticação (Login)
def test_user_login_success(client: TestClient, db_session_override: Session):
    user_password = "LoginUserP@ss1!"
    user_email = "login_user@example.com"
    create_test_user(db_session_override, "Login User", user_email, user_password, phone_number="5511987650015")
    
    response = client.post(
        "/auth/login",
        data={"username": user_email, "password": user_password}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_user_login_invalid_credentials(client: TestClient, db_session_override: Session):
    # Não cria o usuário, então as credenciais serão inválidas
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "anypassword"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Credenciais inválidas" in response.json()["detail"]

def test_user_login_incorrect_password(client: TestClient, db_session_override: Session):
    user_password = "CorrectP@ss1!"
    user_email = "incorrect_pass@example.com"
    create_test_user(db_session_override, "Incorrect Pass User", user_email, user_password, phone_number="5511987650016")
    
    response = client.post(
        "/auth/login",
        data={"username": user_email, "password": "WrongPassword!"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Credenciais inválidas" in response.json()["detail"]

# Testes de Acesso a Rotas Protegidas
def test_protected_route_no_token(client: TestClient):
    response = client.get("/users/me") # Rota protegida
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Não autenticado" in response.json()["detail"]

def test_protected_route_invalid_token(client: TestClient):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Token inválido" in response.json()["detail"]