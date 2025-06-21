# File: backend/tests/integration/briefing/test_briefing_integration_01.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.conftest import create_test_user, get_user_token, create_test_admin_user, get_admin_token # Importa as funções auxiliares

# Importar schemas de briefing para validação se necessário, mas para integração, o foco é a resposta da API
# from src.schemas.briefing_schemas import BriefingCreate, BriefingRead

# Teste para criação de um novo briefing por um usuário autenticado
def test_create_briefing_successfully(client: TestClient, db_session_override: Session):
    user_password = "TestUserP@ss1!"
    user_email = "create_briefing_user@example.com"
    user_name = "Create Briefing User"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    briefing_data = {
        "title": "Briefing do Cliente A - Site Pessoal",
        "status": "Rascunho",
        "content": {"objetivo": "Criar um site portfólio para designers", "publico_alvo": "Estudantes e profissionais recém-formados"}
    }

    response = client.post("/briefings/", json=briefing_data, headers=headers)

    assert response.status_code == 200 # ou 201 Created, dependendo da sua implementação
    response_json = response.json()
    assert response_json["title"] == briefing_data["title"]
    assert response_json["status"] == briefing_data["status"]
    assert response_json["content"] == briefing_data["content"]
    assert "id" in response_json
    assert "user_id" in response_json
    assert response_json["user_id"] == user_credentials.id # Verifica se o briefing foi associado ao usuário correto
    assert "creation_date" in response_json
    assert "update_date" in response_json
    assert "last_edited_by" in response_json
    assert response_json["last_edited_by"] == "user" # O usuário comum criou

# Teste para ler um briefing existente por seu proprietário
def test_read_own_briefing_successfully(client: TestClient, db_session_override: Session):
    user_password = "TestReadP@ss1!"
    user_email = "read_briefing_user@example.com"
    user_name = "Read Briefing User"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    # Primeiro, crie um briefing para o usuário de teste
    create_headers = {"Authorization": f"Bearer {user_token}"}
    create_briefing_data = {
        "title": "Briefing para Leitura Propria",
        "status": "Em Andamento",
        "content": {"secao1": "Conteúdo teste de leitura"}
    }
    create_response = client.post("/briefings/", json=create_briefing_data, headers=create_headers)
    assert create_response.status_code == 200
    briefing_id = create_response.json()["id"]

    # Agora, tente ler o briefing
    read_response = client.get(f"/briefings/{briefing_id}", headers=create_headers)

    assert read_response.status_code == 200
    response_json = read_response.json()
    assert response_json["id"] == briefing_id
    assert response_json["title"] == create_briefing_data["title"]
    assert response_json["user_id"] == user_credentials.id

# Teste para um usuário tentar ler um briefing que não pertence a ele (deve falhar)
def test_read_other_user_briefing_fails(client: TestClient, db_session_override: Session):
    # Usuário 1 (proprietário do briefing)
    user1_password = "UserOneP@ss1!"
    user1_email = "user1_briefing@example.com"
    user1_name = "User One"
    user1_credentials = create_test_user(db_session_override, user1_name, user1_email, user1_password)
    user1_token = get_user_token(client, db_session_override, email=user1_credentials.email, password=user1_password)

    # Crie um briefing para o Usuário 1
    briefing_data = {
        "title": "Briefing do Usuário 1",
        "status": "Finalizado",
        "content": {"info": "Conteúdo do briefing do usuário 1"}
    }
    create_response = client.post("/briefings/", json=briefing_data, headers={"Authorization": f"Bearer {user1_token}"})
    assert create_response.status_code == 200
    briefing_id = create_response.json()["id"]

    # Usuário 2 (tentará ler o briefing do Usuário 1)
    user2_password = "UserTwoP@ss1!"
    user2_email = "user2_briefing@example.com"
    user2_name = "User Two"
    user2_credentials = create_test_user(db_session_override, user2_name, user2_email, user2_password)
    user2_token = get_user_token(client, db_session_override, email=user2_credentials.email, password=user2_password)

    headers_user2 = {"Authorization": f"Bearer {user2_token}"}
    response = client.get(f"/briefings/{briefing_id}", headers=headers_user2)

    # Deve retornar 404 (Não Encontrado) ou 403 (Proibido)
    # 404 é comum para não revelar a existência do recurso a usuários não autorizados
    assert response.status_code in [404, 403]
    assert "detail" in response.json()

# Teste para tentar criar um briefing sem autenticação (deve falhar)
def test_create_briefing_unauthenticated_fails(client: TestClient, db_session_override: Session):
    briefing_data = {
        "title": "Briefing Sem Autenticação",
        "status": "Rascunho",
        "content": {"dados": "teste"}
    }
    response = client.post("/briefings/", json=briefing_data) # Sem cabeçalho de autorização

    assert response.status_code == 401 # Não Autorizado
    assert response.json()["detail"] == "Não foi possível validar as credenciais"

# Teste para ler um briefing que não existe
def test_read_non_existent_briefing_fails(client: TestClient, db_session_override: Session):
    user_password = "TestNonExistentP@ss1!"
    user_email = "non_existent_briefing_user@example.com"
    user_name = "Non Existent Briefing User"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    headers = {"Authorization": f"Bearer {user_token}"}
    non_existent_briefing_id = 999999999 # ID que certamente não existe

    response = client.get(f"/briefings/{non_existent_briefing_id}", headers=headers)

    assert response.status_code == 404 # Não Encontrado
    assert response.json()["detail"] == "Briefing não encontrado."

# Teste para listar briefings de um usuário
def test_list_briefings_for_user_successfully(client: TestClient, db_session_override: Session):
    user_password = "TestListP@ss1!"
    user_email = "list_briefing_user@example.com"
    user_name = "List Briefing User"
    user_credentials = create_test_user(db_session_override, user_name, user_email, user_password)
    user_token = get_user_token(client, db_session_override, email=user_credentials.email, password=user_password)

    headers = {"Authorization": f"Bearer {user_token}"}

    # Crie múltiplos briefings para o mesmo usuário
    briefing_data_1 = {"title": "Briefing 1 do Usuário", "status": "Rascunho", "content": {}}
    briefing_data_2 = {"title": "Briefing 2 do Usuário", "status": "Concluído", "content": {}}

    client.post("/briefings/", json=briefing_data_1, headers=headers)
    client.post("/briefings/", json=briefing_data_2, headers=headers)

    response = client.get("/briefings/", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) >= 2 # Pode haver outros briefings de testes anteriores, mas deve ter pelo menos 2 novos

    # Verifique se os briefings criados estão na lista
    titles = [b["title"] for b in response_json]
    assert "Briefing 1 do Usuário" in titles
    assert "Briefing 2 do Usuário" in titles

# Teste para listar briefings sem autenticação (deve falhar)
def test_list_briefings_unauthenticated_fails(client: TestClient):
    response = client.get("/briefings/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais"