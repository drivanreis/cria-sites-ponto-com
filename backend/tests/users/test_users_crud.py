# File: backend/tests/users/test_users_crud.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import create_test_user, get_user_token

from src.cruds.user_cruds import get_user, update_user
from src.models.user_models import User


# Teste de leitura de usuário específico como o próprio usuário
def test_read_specific_user_as_self(client: TestClient, db_session_override: Session):
    user_password = "SelfRead1234!"
    user_email = "self_read@example.com"
    # Crie o usuário UMA VEZ no início do teste
    user_credentials = create_test_user(db_session_override, "Self Read User", user_email, user_password)
    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get(f"/users/me", headers=headers) # Rota para pegar o próprio usuário

    assert response.status_code == 200
    assert response.json()["email"] == user_email
    assert response.json()["name"] == "Self Read User"

# Teste de atualização de usuário como o próprio usuário
def test_update_user_as_self(client: TestClient, db_session_override: Session):
    user_password = "SelfUpdate1234!"
    user_email = "self_update@example.com"
    # Crie o usuário UMA VEZ no início do teste
    user_credentials = create_test_user(db_session_override, "Self Update User", user_email, user_password)
    user_token = get_user_token(client, db_session_override, user_credentials.email, user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    updated_data = {"name": "Updated Self Name", "phone_number": "5511987654321"} # Adicionando phone_number

    # A rota /users/{user_id} deve ser capaz de lidar com a atualização
    response = client.put(f"/users/{user_credentials.id}", json=updated_data, headers=headers)

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Self Name"
    assert response.json()["phone_number"] == "5511987654321"

    # Opcional: Verificar se o usuário foi realmente atualizado no banco de dados
    # CORREÇÃO AQUI: Use o modelo User e a função get_user se necessário, ou query direta
    updated_user_in_db = db_session_override.query(User).filter(User.id == user_credentials.id).first()
    assert updated_user_in_db.name == "Updated Self Name"
    assert updated_user_in_db.phone_number == "5511987654321"

# O teste para "Número de telefone já registrado" que você adicionou
def test_create_user_duplicate_phone_number(client: TestClient, db_session_override: Session):
    # Primeiro, crie um usuário com um número de telefone específico
    user_data_initial = {
        "name": "Usuario Telefone Original",
        "email": "telefone.original@example.com",
        "password": "SenhaTeste123!",
        "phone_number": "5511998877665"
    }
    response_initial = client.post("/users/", json=user_data_initial)
    assert response_initial.status_code == 201

    # Tente criar outro usuário com o MESMO número de telefone
    duplicate_phone_data = {
        "name": "Usuario Telefone Duplicado",
        "email": "telefone.duplicado@example.com", # Diferente email para testar só o telefone
        "password": "OutraSenha123!",
        "phone_number": "5511998877665" # Número de telefone duplicado
    }
    response_duplicate = client.post(
        "/users/",
        json=duplicate_phone_data
    )
    assert response_duplicate.status_code == 409
    assert response_duplicate.json()["detail"] == "Número de telefone já registrado"