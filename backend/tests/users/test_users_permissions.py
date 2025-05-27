# File: backend/tests/users/test_users_permissions.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.schemas.user import UserUpdate
from src.models.user import User
from tests.conftest import create_test_user, create_test_admin_user, get_admin_token, get_user_token

def test_list_users(client: TestClient, db_session_override: Session):
    admin_password = "AdListUser123!"
    admin_user = create_test_admin_user(db_session_override, "list_users_admin", admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_user.username, admin_password)

    # Cria alguns usuários comuns para listar
    create_test_user(db_session_override, "User A", "user_a_list@example.com", "ListUserA123!")
    create_test_user(db_session_override, "User B", "user_b_list@example.com", "ListUserB123!")

    response = client.get("/users/", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    users_data = response.json()
    assert isinstance(users_data, list)
    assert len(users_data) == 2 

# Teste para listar usuários como usuário comum (proibido)
# Removido: @pytest.mark.asyncio
# Removido: async def
def test_list_users_as_regular_user_forbidden(client: TestClient, db_session_override: Session): # Tipo do cliente alterado
    user_password = "Forbidden1234!" # Senha ajustada
    user = create_test_user(db_session_override, "List Forbidden", "list_forbidden@example.com", user_password) # Removido await
    user_token = get_user_token(client, db_session_override, user.email, user_password) # Removido await

    response = client.get("/users/", headers={"Authorization": f"Bearer {user_token}"}) # Removido await
    assert response.status_code == 403 # Proibido


# Teste para ler um usuário específico como outro usuário (proibido)
# Removido: @pytest.mark.asyncio
# Removido: async def
def test_read_specific_user_as_other_user_forbidden(client: TestClient, db_session_override: Session): # Tipo do cliente alterado
    user_a_password = "UserA1234!" # Senha ajustada
    user_a = create_test_user(db_session_override, "User A", "user_a_read@example.com", user_a_password) # Removido await

    user_b_password = "UserB1234!"
    user_b = create_test_user(db_session_override, "User B", "user_b_read@example.com", user_b_password) # Removido await

    # user_a_token = get_user_token(client, db_session_override, user_a.email, user_a_password) # Não é necessário aqui
    user_b_token = get_user_token(client, db_session_override, user_b.email, user_b_password) # Removido await

    response = client.get(f"/users/{user_a.id}", headers={"Authorization": f"Bearer {user_b_token}"}) # Removido await
    assert response.status_code == 403 # Proibido


# Teste para ler um usuário específico como administrador
# Removido: @pytest.mark.asyncio
# Removido: async def
def test_read_specific_user_as_admin(client: TestClient, db_session_override: Session): # Tipo do cliente alterado
    admin_password = "AdReadUser123!" # Senha ajustada
    admin_user = create_test_admin_user(db_session_override, "admin_read_user", admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_user.username, admin_password) # Removido await

    user_to_read_password = "UserRead123!"
    user_to_read = create_test_user(db_session_override, "User Read By Admin", "user_read_admin@example.com", user_to_read_password) # Removido await

    response = client.get(f"/users/{user_to_read.id}", headers={"Authorization": f"Bearer {admin_token}"}) # Removido await
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == "user_read_admin@example.com"
    assert user_data["name"] == "User Read By Admin"


# Teste para atualizar um usuário como outro usuário (proibido)
# Removido: @pytest.mark.asyncio
# Removido: async def
def test_update_user_as_other_user_forbidden(client: TestClient, db_session_override: Session): # Tipo do cliente alterado
    user_a_password = "UserAUpdate1234!" # Senha ajustada
    user_a = create_test_user(db_session_override, "User A Update", "user_a_update@example.com", user_a_password) # Removido await

    user_b_password = "UserBUpdate1234!"
    user_b = create_test_user(db_session_override, "User B Update", "user_b_update@example.com", user_b_password) # Removido await

    # user_a_token = get_user_token(client, db_session_override, user_a.email, user_a_password) # Não é necessário aqui
    user_b_token = get_user_token(client, db_session_override, user_b.email, user_b_password) # Removido await

    update_data = {"name": "Updated User A", "email": "updated.user_a@example.com"} # email deve ser único
    response = client.put(f"/users/{user_a.id}", json=update_data, headers={"Authorization": f"Bearer {user_b_token}"}) # Removido await
    assert response.status_code == 403 # Proibido


# Teste para atualizar um usuário como administrador
# Removido: @pytest.mark.asyncio
# Removido: async def
def test_update_user_as_admin(client: TestClient, db_session_override: Session): # Tipo do cliente alterado
    admin_password = "AdUpdUser123!" # Senha ajustada
    admin_user = create_test_admin_user(db_session_override, "admin_update_user", admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_user.username, admin_password) # Removido await

    user_to_update_password = "UserUpd123!"
    user_to_update = create_test_user(db_session_override, "User To Update", "user_to_update@example.com", user_to_update_password) # Removido await

    updated_name = "Updated User Admin"
    updated_email = "updated.user.admin@example.com"
    update_data = UserUpdate(name=updated_name, email=updated_email).model_dump(exclude_unset=True)

    response = client.put(f"/users/{user_to_update.id}", json=update_data, headers={"Authorization": f"Bearer {admin_token}"}) # Removido await
    assert response.status_code == 200
    updated_user_data = response.json()
    assert updated_user_data["name"] == updated_name
    assert updated_user_data["email"] == updated_email

    # Verifique se o usuário foi realmente atualizado no banco de dados
    updated_user_in_db = db_session_override.query(User).filter(User.id == user_to_update.id).first()
    assert updated_user_in_db.name == updated_name
    assert updated_user_in_db.email == updated_email


# Teste para deletar um usuário como outro usuário (proibido)
# Removido: @pytest.mark.asyncio
# Removido: async def
def test_delete_user_as_other_user_forbidden(client: TestClient, db_session_override: Session): # Tipo do cliente alterado
    user_a_password = "UserADelete1234!" # Senha ajustada
    user_a = create_test_user(db_session_override, "User A Delete", "user_a_delete@example.com", user_a_password) # Removido await

    user_b_password = "UserBDelete1234!"
    user_b = create_test_user(db_session_override, "User B Delete", "user_b_delete@example.com", user_b_password) # Removido await

    # user_a_token = get_user_token(client, db_session_override, user_a.email, user_a_password) # Não é necessário aqui
    user_b_token = get_user_token(client, db_session_override, user_b.email, user_b_password) # Removido await

    response = client.delete(f"/users/{user_a.id}", headers={"Authorization": f"Bearer {user_b_token}"}) # Removido await
    assert response.status_code == 403 # Proibido

    # Verifique se o usuário A ainda existe
    user_a_exists = db_session_override.query(User).filter(User.id == user_a.id).first()
    assert user_a_exists is not None


# Teste para deletar um usuário como administrador
# Removido: @pytest.mark.asyncio
# Removido: async def
def test_delete_user_as_admin(client: TestClient, db_session_override: Session): # Tipo do cliente alterado
    admin_password = "AdDelUser123!" # Senha ajustada
    admin_user = create_test_admin_user(db_session_override, "admin_delete_user", admin_password)
    admin_token = get_admin_token(client, db_session_override, admin_user.username, admin_password) # Removido await

    user_to_delete_password = "UserDel123!"
    user_to_delete = create_test_user(db_session_override, "User To Delete", "user_to_delete@example.com", user_to_delete_password) # Removido await

    response = client.delete(f"/users/{user_to_delete.id}", headers={"Authorization": f"Bearer {admin_token}"}) # Removido await
    assert response.status_code == 204 # No Content, indicando sucesso na deleção

    # Verifique se o usuário foi realmente deletado do banco de dados
    deleted_user_in_db = db_session_override.query(User).filter(User.id == user_to_delete.id).first()
    assert deleted_user_in_db is None