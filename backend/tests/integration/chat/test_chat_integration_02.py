# File: backend/tests/integration/briefing/test_briefing_integration_02.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.conftest import create_test_user, get_user_token, create_test_admin_user, get_admin_token

# Teste para atualização de um briefing por seu proprietário
def test_update_own_briefing_successfully(client: TestClient, db_session_override: Session):
    user_password = "TestUpdateP@ss1!"
    user_email = "update_briefing_user@example.com"
    user_name = "Update Briefing User"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    # Crie um briefing inicial
    initial_briefing_data = {
        "title": "Briefing Inicial do Cliente",
        "status": "Rascunho",
        "content": {"objetivo": "Site simples"}
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    create_response = client.post("/briefings/", json=initial_briefing_data, headers=headers)
    assert create_response.status_code == 200
    briefing_id = create_response.json()["id"]

    # Dados para atualização
    updated_briefing_data = {
        "title": "Briefing Atualizado do Cliente",
        "status": "Em Andamento",
        "content": {"objetivo": "Site e-commerce", "detalhes": "Adicionar carrinho de compras"}
    }

    update_response = client.put(f"/briefings/{briefing_id}", json=updated_briefing_data, headers=headers)

    assert update_response.status_code == 200
    response_json = update_response.json()
    assert response_json["id"] == briefing_id
    assert response_json["title"] == updated_briefing_data["title"]
    assert response_json["status"] == updated_briefing_data["status"]
    assert response_json["content"] == updated_briefing_data["content"]
    assert response_json["user_id"] == user_credentials.id
    assert response_json["last_edited_by"] == "user" # O usuário comum atualizou

# Teste para atualização de um briefing por um administrador
def test_update_briefing_by_admin_successfully(client: TestClient, db_session_override: Session):
    user_password = "UserForAdminUpdateP@ss1!"
    user_email = "user_for_admin_briefing_update@example.com"
    user_name = "User for Admin Update"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    # Crie um briefing para o usuário comum
    initial_briefing_data = {
        "title": "Briefing do Usuário para Admin",
        "status": "Rascunho",
        "content": {"projeto": "Blog pessoal"}
    }
    create_response = client.post("/briefings/", json=initial_briefing_data, headers={"Authorization": f"Bearer {user_token}"})
    assert create_response.status_code == 200
    briefing_id = create_response.json()["id"]

    # Crie um usuário administrador e obtenha seu token
    admin_password = "AdminUpdateP@ss1!"
    admin_email = "admin_briefing_update@example.com"
    admin_name = "Admin Briefing Update"
    admin_credentials = create_test_admin_user(db_session_override, admin_name, admin_email, admin_password)
    admin_token = get_admin_token(client, db_session_override, username=admin_credentials.email, password=admin_password)

    # Dados para atualização pelo admin
    updated_briefing_data = {
        "title": "Briefing Atualizado pelo Admin",
        "status": "Concluído",
        "content": {"projeto": "Blog pessoal - Finalizado", "observacoes_admin": "Revisado e aprovado"}
    }
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    update_response = client.put(f"/briefings/{briefing_id}", json=updated_briefing_data, headers=admin_headers)

    assert update_response.status_code == 200
    response_json = update_response.json()
    assert response_json["id"] == briefing_id
    assert response_json["title"] == updated_briefing_data["title"]
    assert response_json["status"] == updated_briefing_data["status"]
    assert response_json["content"] == updated_briefing_data["content"]
    assert response_json["user_id"] == user_credentials.id
    assert response_json["last_edited_by"] == "admin" # O admin atualizou

# Teste para um usuário comum tentar atualizar um briefing que não pertence a ele (deve falhar)
def test_update_other_user_briefing_fails(client: TestClient, db_session_override: Session):
    user1_password = "User1UpdateP@ss1!"
    user1_email = "user1_update_briefing@example.com"
    user1_name = "User 1 Update Briefing"
    user1_credentials = create_test_user(db_session_override, user1_name, user1_email, user1_password)
    user1_token = get_user_token(client, db_session_override, email=user1_credentials.email, password=user1_password)

    initial_briefing_data = {
        "title": "Briefing do Usuário 1",
        "status": "Rascunho",
        "content": {"info": "Conteúdo do briefing do usuário 1"}
    }
    create_response = client.post("/briefings/", json=initial_briefing_data, headers={"Authorization": f"Bearer {user1_token}"})
    assert create_response.status_code == 200
    briefing_id = create_response.json()["id"]

    user2_password = "User2UpdateP@ss1!"
    user2_email = "user2_update_briefing@example.com"
    user2_name = "User 2 Update Briefing"
    user2_credentials = create_test_user(db_session_override, user2_name, user2_email, user2_password)
    user2_token = get_user_token(client, db_session_override, email=user2_credentials.email, password=user2_password)

    updated_briefing_data = {
        "title": "Tentativa de Atualização",
        "status": "Finalizado",
        "content": {"tentativa": "invasão"}
    }
    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    response = client.put(f"/briefings/{briefing_id}", json=updated_briefing_data, headers=headers_user2)

    assert response.status_code in [404, 403]
    assert "detail" in response.json()

# Teste para deletar um briefing por seu proprietário
def test_delete_own_briefing_successfully(client: TestClient, db_session_override: Session):
    user_password = "TestDeleteP@ss1!"
    user_email = "delete_briefing_user@example.com"
    user_name = "Delete Briefing User"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    initial_briefing_data = {
        "title": "Briefing para Deletar Proprio",
        "status": "Rascunho",
        "content": {"item": "a ser removido"}
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    create_response = client.post("/briefings/", json=initial_briefing_data, headers=headers)
    assert create_response.status_code == 200
    briefing_id = create_response.json()["id"]

    delete_response = client.delete(f"/briefings/{briefing_id}", headers=headers)
    assert delete_response.status_code == 204 # No Content

    # Verifique se o briefing foi realmente deletado
    read_response = client.get(f"/briefings/{briefing_id}", headers=headers)
    assert read_response.status_code == 404 # Não Encontrado

# Teste para deletar um briefing por um administrador
def test_delete_briefing_by_admin_successfully(client: TestClient, db_session_override: Session):
    user_password = "UserForAdminDeleteP@ss1!"
    user_email = "user_for_admin_briefing_delete@example.com"
    user_name = "User for Admin Delete"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    initial_briefing_data = {
        "title": "Briefing do Usuário para Delete Admin",
        "status": "Rascunho",
        "content": {"projeto": "Site para teste de admin"}
    }
    create_response = client.post("/briefings/", json=initial_briefing_data, headers={"Authorization": f"Bearer {user_token}"})
    assert create_response.status_code == 200
    briefing_id = create_response.json()["id"]

    admin_password = "AdminDeleteP@ss1!"
    admin_email = "admin_briefing_delete@example.com"
    admin_name = "Admin Briefing Delete"
    admin_credentials = create_test_admin_user(db_session_override, admin_name, admin_email, admin_password)
    admin_token = get_admin_token(client, db_session_override, username=admin_credentials.email, password=admin_password)

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    delete_response = client.delete(f"/briefings/{briefing_id}", headers=admin_headers)
    assert delete_response.status_code == 204 # No Content

    # Verifique se o briefing foi realmente deletado pelo admin
    read_response = client.get(f"/briefings/{briefing_id}", headers=admin_headers)
    assert read_response.status_code == 404 # Não Encontrado

# Teste para um usuário comum tentar deletar um briefing que não pertence a ele (deve falhar)
def test_delete_other_user_briefing_fails(client: TestClient, db_session_override: Session):
    user1_password = "User1DeleteP@ss1!"
    user1_email = "user1_delete_briefing@example.com"
    user1_name = "User 1 Delete Briefing"
    user1_credentials = create_test_user(db_session_override, user1_name, user1_email, user1_password)
    user1_token = get_user_token(client, db_session_override, email=user1_credentials.email, password=user1_password)

    initial_briefing_data = {
        "title": "Briefing do Usuário 1 para Delete",
        "status": "Rascunho",
        "content": {"info": "Conteúdo do briefing do usuário 1"}
    }
    create_response = client.post("/briefings/", json=initial_briefing_data, headers={"Authorization": f"Bearer {user1_token}"})
    assert create_response.status_code == 200
    briefing_id = create_response.json()["id"]

    user2_password = "User2DeleteP@ss1!"
    user2_email = "user2_delete_briefing@example.com"
    user2_name = "User 2 Delete Briefing"
    user2_credentials = create_test_user(db_session_override, user2_name, user2_email, user2_password)
    user2_token = get_user_token(client, db_session_override, email=user2_credentials.email, password=user2_password)

    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    response = client.delete(f"/briefings/{briefing_id}", headers=headers_user2)

    assert response.status_code in [404, 403]
    assert "detail" in response.json()

# Teste para tentar atualizar um briefing sem autenticação (deve falhar)
def test_update_briefing_unauthenticated_fails(client: TestClient, db_session_override: Session):
    user_password = "UserNoAuthUpdateP@ss1!"
    user_email = "user_no_auth_briefing_update@example.com"
    user_name = "User No Auth Update"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    initial_briefing_data = {
        "title": "Briefing sem auth para atualizar",
        "status": "Rascunho",
        "content": {"dados": "teste"}
    }
    create_response = client.post("/briefings/", json=initial_briefing_data, headers={"Authorization": f"Bearer {user_token}"})
    assert create_response.status_code == 200
    briefing_id = create_response.json()["id"]

    updated_briefing_data = {
        "title": "Tentativa de Atualização sem autenticação",
        "status": "Finalizado",
        "content": {"dados": "teste atualizado"}
    }
    response = client.put(f"/briefings/{briefing_id}", json=updated_briefing_data) # Sem cabeçalho de autorização

    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais"

# Teste para tentar deletar um briefing sem autenticação (deve falhar)
def test_delete_briefing_unauthenticated_fails(client: TestClient, db_session_override: Session):
    user_password = "UserNoAuthDeleteP@ss1!"
    user_email = "user_no_auth_briefing_delete@example.com"
    user_name = "User No Auth Delete"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    initial_briefing_data = {
        "title": "Briefing sem auth para deletar",
        "status": "Rascunho",
        "content": {"dados": "a serem deletados"}
    }
    create_response = client.post("/briefings/", json=initial_briefing_data, headers={"Authorization": f"Bearer {user_token}"})
    assert create_response.status_code == 200
    briefing_id = create_response.json()["id"]

    response = client.delete(f"/briefings/{briefing_id}") # Sem cabeçalho de autorização

    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais"