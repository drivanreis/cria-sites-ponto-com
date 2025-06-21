# File: backend/tests/integration/character/test_character_integration_02.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.conftest import create_test_user, get_user_token, create_test_admin_user, get_admin_token

# Teste para atualização de um personagem por seu proprietário
def test_update_own_character_successfully(client: TestClient, db_session_override: Session):
    user_password = "CharUpdateOwnP@ss1!"
    user_email = "update_own_char_user@example.com"
    user_name = "Update Own Character User"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    # Crie um personagem inicial
    initial_character_data = {
        "name": "Personagem Inicial",
        "description": "Uma descrição básica.",
        "image_url": "http://example.com/initial_char.png"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    create_response = client.post("/characters/", json=initial_character_data, headers=headers)
    assert create_response.status_code == 200
    character_id = create_response.json()["id"]

    # Dados para atualização
    updated_character_data = {
        "name": "Personagem Atualizado",
        "description": "Uma descrição mais detalhada.",
        "image_url": "http://example.com/updated_char.png"
    }

    update_response = client.put(f"/characters/{character_id}", json=updated_character_data, headers=headers)

    assert update_response.status_code == 200
    response_json = update_response.json()
    assert response_json["id"] == character_id
    assert response_json["name"] == updated_character_data["name"]
    assert response_json["description"] == updated_character_data["description"]
    assert response_json["image_url"] == updated_character_data["image_url"]
    assert response_json["user_id"] == user_credentials.id

# Teste para atualização de um personagem por um administrador
def test_update_character_by_admin_successfully(client: TestClient, db_session_override: Session):
    user_password = "UserForAdminCharUpdateP@ss1!"
    user_email = "user_for_admin_char_update@example.com"
    user_name = "User for Admin Char Update"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    # Crie um personagem para o usuário comum
    initial_character_data = {
        "name": "Personagem do Usuário para Admin",
        "description": "Desc do user.",
        "image_url": "http://example.com/user_char_admin_test.png"
    }
    create_response = client.post("/characters/", json=initial_character_data, headers={"Authorization": f"Bearer {user_token}"})
    assert create_response.status_code == 200
    character_id = create_response.json()["id"]

    # Crie um usuário administrador e obtenha seu token
    admin_password = "AdminCharUpdateP@ss1!"
    admin_email = "admin_char_update@example.com"
    admin_name = "Admin Character Update"
    admin_credentials = create_test_admin_user(db_session_override, admin_name, admin_email, admin_password)
    admin_token = get_admin_token(client, db_session_override, username=admin_credentials.email, password=admin_password)

    # Dados para atualização pelo admin
    updated_character_data = {
        "name": "Personagem Atualizado pelo Admin",
        "description": "Desc atualizada pelo admin.",
        "image_url": "http://example.com/admin_updated_char.png"
    }
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    update_response = client.put(f"/characters/{character_id}", json=updated_character_data, headers=admin_headers)

    assert update_response.status_code == 200
    response_json = update_response.json()
    assert response_json["id"] == character_id
    assert response_json["name"] == updated_character_data["name"]
    assert response_json["description"] == updated_character_data["description"]
    assert response_json["image_url"] == updated_character_data["image_url"]
    assert response_json["user_id"] == user_credentials.id

# Teste para um usuário comum tentar atualizar um personagem que não pertence a ele (deve falhar)
def test_update_other_user_character_fails(client: TestClient, db_session_override: Session):
    user1_password = "User1CharUpdateP@ss1!"
    user1_email = "user1_update_char@example.com"
    user1_name = "User 1 Update Char"
    user1_credentials = create_test_user(db_session_override, user1_name, user1_email, user1_password)
    user1_token = get_user_token(client, db_session_override, email=user1_credentials.email, password=user1_password)

    initial_character_data = {
        "name": "Personagem do Usuário 1",
        "description": "Desc do user 1.",
        "image_url": "http://example.com/user1_char.png"
    }
    create_response = client.post("/characters/", json=initial_character_data, headers={"Authorization": f"Bearer {user1_token}"})
    assert create_response.status_code == 200
    character_id = create_response.json()["id"]

    user2_password = "User2CharUpdateP@ss1!"
    user2_email = "user2_update_char@example.com"
    user2_name = "User 2 Update Char"
    user2_credentials = create_test_user(db_session_override, user2_name, user2_email, user2_password)
    user2_token = get_user_token(client, db_session_override, email=user2_credentials.email, password=user2_password)

    updated_character_data = {
        "name": "Tentativa de Atualização Caracter",
        "description": "Descrição de tentativa.",
        "image_url": "http://example.com/attempt_char.png"
    }
    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    response = client.put(f"/characters/{character_id}", json=updated_character_data, headers=headers_user2)

    assert response.status_code in [404, 403]
    assert "detail" in response.json()

# Teste para deletar um personagem por seu proprietário
def test_delete_own_character_successfully(client: TestClient, db_session_override: Session):
    user_password = "CharDeleteOwnP@ss1!"
    user_email = "delete_own_char_user@example.com"
    user_name = "Delete Own Character User"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    initial_character_data = {
        "name": "Personagem para Deletar Proprio",
        "description": "Este será deletado.",
        "image_url": "http://example.com/to_delete_char.png"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    create_response = client.post("/characters/", json=initial_character_data, headers=headers)
    assert create_response.status_code == 200
    character_id = create_response.json()["id"]

    delete_response = client.delete(f"/characters/{character_id}", headers=headers)
    assert delete_response.status_code == 204 # No Content

    # Verifique se o personagem foi realmente deletado
    read_response = client.get(f"/characters/{character_id}", headers=headers)
    assert read_response.status_code == 404 # Não Encontrado

# Teste para deletar um personagem por um administrador
def test_delete_character_by_admin_successfully(client: TestClient, db_session_override: Session):
    user_password = "UserForAdminCharDeleteP@ss1!"
    user_email = "user_for_admin_char_delete@example.com"
    user_name = "User for Admin Char Delete"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    initial_character_data = {
        "name": "Personagem do Usuário para Delete Admin",
        "description": "Será deletado pelo admin.",
        "image_url": "http://example.com/admin_delete_char.png"
    }
    create_response = client.post("/characters/", json=initial_character_data, headers={"Authorization": f"Bearer {user_token}"})
    assert create_response.status_code == 200
    character_id = create_response.json()["id"]

    admin_password = "AdminCharDeleteP@ss1!"
    admin_email = "admin_char_delete@example.com"
    admin_name = "Admin Character Delete"
    admin_credentials = create_test_admin_user(db_session_override, admin_name, admin_email, admin_password)
    admin_token = get_admin_token(client, db_session_override, username=admin_credentials.email, password=admin_password)

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    delete_response = client.delete(f"/characters/{character_id}", headers=admin_headers)
    assert delete_response.status_code == 204 # No Content

    # Verifique se o personagem foi realmente deletado pelo admin
    read_response = client.get(f"/characters/{character_id}", headers=admin_headers)
    assert read_response.status_code == 404 # Não Encontrado

# Teste para um usuário comum tentar deletar um personagem que não pertence a ele (deve falhar)
def test_delete_other_user_character_fails(client: TestClient, db_session_override: Session):
    user1_password = "User1CharDeleteP@ss1!"
    user1_email = "user1_delete_char@example.com"
    user1_name = "User 1 Delete Char"
    user1_credentials = create_test_user(db_session_override, user1_name, user1_email, user1_password)
    user1_token = get_user_token(client, db_session_override, email=user1_credentials.email, password=user1_password)

    initial_character_data = {
        "name": "Personagem do Usuário 1 para Delete",
        "description": "Este não será deletado por outro user.",
        "image_url": "http://example.com/user1_delete_char.png"
    }
    create_response = client.post("/characters/", json=initial_character_data, headers={"Authorization": f"Bearer {user1_token}"})
    assert create_response.status_code == 200
    character_id = create_response.json()["id"]

    user2_password = "User2CharDeleteP@ss1!"
    user2_email = "user2_delete_char@example.com"
    user2_name = "User 2 Delete Char"
    user2_credentials = create_test_user(db_session_override, user2_name, user2_email, user2_password)
    user2_token = get_user_token(client, db_session_override, email=user2_credentials.email, password=user2_password)

    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    response = client.delete(f"/characters/{character_id}", headers=headers_user2)

    assert response.status_code in [404, 403]
    assert "detail" in response.json()

# Teste para tentar atualizar um personagem sem autenticação (deve falhar)
def test_update_character_unauthenticated_fails(client: TestClient, db_session_override: Session):
    user_password = "UserNoAuthCharUpdateP@ss1!"
    user_email = "user_no_auth_char_update@example.com"
    user_name = "User No Auth Char Update"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    initial_character_data = {
        "name": "Personagem sem auth para atualizar",
        "description": "Desc a ser atualizada.",
        "image_url": "http://example.com/no_auth_update_char.png"
    }
    create_response = client.post("/characters/", json=initial_character_data, headers={"Authorization": f"Bearer {user_token}"})
    assert create_response.status_code == 200
    character_id = create_response.json()["id"]

    updated_character_data = {
        "name": "Tentativa de Atualização sem autenticação",
        "description": "Descrição atualizada.",
        "image_url": "http://example.com/no_auth_updated_char.png"
    }
    response = client.put(f"/characters/{character_id}", json=updated_character_data) # Sem cabeçalho de autorização

    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais"

# Teste para tentar deletar um personagem sem autenticação (deve falhar)
def test_delete_character_unauthenticated_fails(client: TestClient, db_session_override: Session):
    user_password = "UserNoAuthCharDeleteP@ss1!"
    user_email = "user_no_auth_char_delete@example.com"
    user_name = "User No Auth Char Delete"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    initial_character_data = {
        "name": "Personagem sem auth para deletar",
        "description": "Será deletado.",
        "image_url": "http://example.com/no_auth_delete_char.png"
    }
    create_response = client.post("/characters/", json=initial_character_data, headers={"Authorization": f"Bearer {user_token}"})
    assert create_response.status_code == 200
    character_id = create_response.json()["id"]

    response = client.delete(f"/characters/{character_id}") # Sem cabeçalho de autorização

    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais"