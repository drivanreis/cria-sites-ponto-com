# File: backend/tests/integration/character/test_character_integration_01.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.conftest import create_test_user, get_user_token, create_test_admin_user, get_admin_token

# Teste para criação de um novo personagem por um usuário autenticado
def test_create_character_successfully(client: TestClient, db_session_override: Session):
    user_password = "CharCreateP@ss1!"
    user_email = "create_character_user@example.com"
    user_name = "Create Character User"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    character_data = {
        "name": "Capitão Estelar",
        "description": "Um herói intergaláctico com poderes cósmicos.",
        "image_url": "http://example.com/capitao_estelar.png"
    }

    response = client.post("/characters/", json=character_data, headers=headers)

    assert response.status_code == 200 # ou 201 Created
    response_json = response.json()
    assert response_json["name"] == character_data["name"]
    assert response_json["description"] == character_data["description"]
    assert response_json["image_url"] == character_data["image_url"]
    assert "id" in response_json
    assert "user_id" in response_json
    assert response_json["user_id"] == user_credentials.id
    assert "creation_date" in response_json
    assert "update_date" in response_json

# Teste para ler um personagem existente por seu proprietário
def test_read_own_character_successfully(client: TestClient, db_session_override: Session):
    user_password = "CharReadP@ss1!"
    user_email = "read_character_user@example.com"
    user_name = "Read Character User"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    # Primeiro, crie um personagem para o usuário de teste
    create_headers = {"Authorization": f"Bearer {user_token}"}
    create_character_data = {
        "name": "Mago do Tempo",
        "description": "Controla a passagem do tempo.",
        "image_url": "http://example.com/mago_tempo.png"
    }
    create_response = client.post("/characters/", json=create_character_data, headers=create_headers)
    assert create_response.status_code == 200
    character_id = create_response.json()["id"]

    # Agora, tente ler o personagem
    read_response = client.get(f"/characters/{character_id}", headers=create_headers)

    assert read_response.status_code == 200
    response_json = read_response.json()
    assert response_json["id"] == character_id
    assert response_json["name"] == create_character_data["name"]
    assert response_json["user_id"] == user_credentials.id

# Teste para um usuário tentar ler um personagem que não pertence a ele (deve falhar)
def test_read_other_user_character_fails(client: TestClient, db_session_override: Session):
    # Usuário 1 (proprietário do personagem)
    user1_password = "UserOneCharP@ss1!"
    user1_email = "user1_character@example.com"
    user1_name = "User One Character"
    user1_credentials = create_test_user(db_session_override, user1_name, user1_email, user1_password)
    user1_token = get_user_token(client, db_session_override, email=user1_credentials.email, password=user1_password)

    # Crie um personagem para o Usuário 1
    character_data = {
        "name": "Cavaleiro Sombrio",
        "description": "Guardião da noite eterna.",
        "image_url": "http://example.com/cavaleiro_sombrio.png"
    }
    create_response = client.post("/characters/", json=character_data, headers={"Authorization": f"Bearer {user1_token}"})
    assert create_response.status_code == 200
    character_id = create_response.json()["id"]

    # Usuário 2 (tentará ler o personagem do Usuário 1)
    user2_password = "UserTwoCharP@ss1!"
    user2_email = "user2_character@example.com"
    user2_name = "User Two Character"
    user2_credentials = create_test_user(db_session_override, user2_name, user2_email, user2_password)
    user2_token = get_user_token(client, db_session_override, email=user2_credentials.email, password=user2_password)

    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    response = client.get(f"/characters/{character_id}", headers=headers_user2)

    # Deve retornar 404 (Não Encontrado) ou 403 (Proibido)
    assert response.status_code in [404, 403]
    assert "detail" in response.json()

# Teste para tentar criar um personagem sem autenticação (deve falhar)
def test_create_character_unauthenticated_fails(client: TestClient, db_session_override: Session):
    character_data = {
        "name": "Personagem Sem Autenticação",
        "description": "Um personagem que não deveria existir.",
        "image_url": "http://example.com/no_auth_char.png"
    }
    response = client.post("/characters/", json=character_data) # Sem cabeçalho de autorização

    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais"

# Teste para ler um personagem que não existe
def test_read_non_existent_character_fails(client: TestClient, db_session_override: Session):
    user_password = "CharNonExistentP@ss1!"
    user_email = "non_existent_char_user@example.com"
    user_name = "Non Existent Character User"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    non_existent_character_id = 999999999 # ID que certamente não existe

    response = client.get(f"/characters/{non_existent_character_id}", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Personagem não encontrado."

# Teste para listar personagens de um usuário
def test_list_characters_for_user_successfully(client: TestClient, db_session_override: Session):
    user_password = "CharListP@ss1!"
    user_email = "list_character_user@example.com"
    user_name = "List Character User"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    headers = {"Authorization": f"Bearer {user_token}"}

    # Crie múltiplos personagens para o mesmo usuário
    character_data_1 = {"name": "Guerreiro Anão", "description": "Lutador forte.", "image_url": "http://example.com/anao.png"}
    character_data_2 = {"name": "Elfa Arqueira", "description": "Atiradora precisa.", "image_url": "http://example.com/elfa.png"}

    client.post("/characters/", json=character_data_1, headers=headers)
    client.post("/characters/", json=character_data_2, headers=headers)

    response = client.get("/characters/", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) >= 2

    # Verifique se os personagens criados estão na lista
    names = [c["name"] for c in response_json]
    assert "Guerreiro Anão" in names
    assert "Elfa Arqueira" in names

# Teste para listar personagens sem autenticação (deve falhar)
def test_list_characters_unauthenticated_fails(client: TestClient):
    response = client.get("/characters/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais"