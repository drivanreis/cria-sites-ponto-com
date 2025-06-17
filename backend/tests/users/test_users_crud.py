# File: backend/tests/cruds/test_user_cruds.py

import pytest
from sqlalchemy.orm import Session
# from sqlalchemy.exc import IntegrityError # Removido, pois o CRUD agora levanta HTTPException
from fastapi import HTTPException, status # Importado para capturar HTTPException

# Import the CRUD functions to be tested
from src.cruds import user_cruds 

# Import necessary models and schemas
from src.models.user_models import User
from src.schemas.user_schemas import UserCreate, UserUpdate

# Import security utilities for password handling verification
from src.core.security import get_password_hash, verify_password

# Import fixture for database session override (from conftest)
from tests.conftest import create_test_user # Use this helper to pre-populate users

# --- Funções Auxiliares para Geração de Dados de Teste ---
# Adicionei um gerador de telefone para garantir que sejam únicos e válidos
_phone_number_counter = 0
def get_unique_phone_number() -> str:
    global _phone_number_counter
    _phone_number_counter += 1
    # Formato com 13 dígitos para se adequar à nova validação (12 a 14 números)
    # Ex: 5511987654321, 5511987654322, etc.
    return f"5511987654{_phone_number_counter:03d}" 

# --- Tests for get_user ---

def test_get_user_exists(db_session_override: Session):
    # Arrange: Create a user
    user_data = UserCreate(
        name="Test User Get",
        email="get@example.com",
        phone_number=get_unique_phone_number(), # Usar função auxiliar
        password="SecurePass123!" # Senha forte
    )
    db_user = user_cruds.create_user(db_session_override, user_data)
    
    # Act: Get the user by ID
    fetched_user = user_cruds.get_user(db_session_override, db_user.id)
    
    # Assert
    assert fetched_user is not None
    assert fetched_user.id == db_user.id
    assert fetched_user.email == "get@example.com"
    assert fetched_user.phone_number == user_data.phone_number # Incluir asserção para phone_number

def test_get_user_not_exists(db_session_override: Session):
    # Act: Try to get a user with a non-existent ID
    fetched_user = user_cruds.get_user(db_session_override, 99999) # Assuming 99999 is a non-existent ID
    
    # Assert
    assert fetched_user is None

# --- Tests for get_user_by_email ---

def test_get_user_by_email_exists(db_session_override: Session):
    # Arrange: Create a user
    user_data = UserCreate(
        name="Test Email User",
        email="email@example.com",
        phone_number=get_unique_phone_number(), # Usar função auxiliar
        password="EmailPass123!" # Senha forte
    )
    user_cruds.create_user(db_session_override, user_data)
    
    # Act: Get the user by email
    fetched_user = user_cruds.get_user_by_email(db_session_override, "email@example.com")
    
    # Assert
    assert fetched_user is not None
    assert fetched_user.email == "email@example.com"

def test_get_user_by_email_not_exists(db_session_override: Session):
    # Act: Try to get a user with a non-existent email
    fetched_user = user_cruds.get_user_by_email(db_session_override, "nonexistent@example.com")
    
    # Assert
    assert fetched_user is None

# --- Tests for get_user_by_phone_number ---

def test_get_user_by_phone_number_exists(db_session_override: Session):
    # Arrange: Create a user
    phone_num = get_unique_phone_number() # Gerar e usar
    user_data = UserCreate(
        name="Test Phone User",
        email="phone@example.com",
        phone_number=phone_num,
        password="PhonePass123!" # Senha forte
    )
    user_cruds.create_user(db_session_override, user_data)
    
    # Act: Get the user by phone number
    fetched_user = user_cruds.get_user_by_phone_number(db_session_override, phone_num)
    
    # Assert
    assert fetched_user is not None
    assert fetched_user.phone_number == phone_num

def test_get_user_by_phone_number_not_exists(db_session_override: Session):
    # Act: Try to get a user with a non-existent phone number
    fetched_user = user_cruds.get_user_by_phone_number(db_session_override, "999999999999") # 12 dígitos, mas não existe
    
    # Assert
    assert fetched_user is None

# --- Tests for get_users ---

def test_get_users_empty_db(db_session_override: Session):
    # Act: Get users from an empty database
    users = user_cruds.get_users(db_session_override)
    
    # Assert
    assert isinstance(users, list)
    assert len(users) == 0

def test_get_users_with_data(db_session_override: Session):
    # Arrange: Create multiple users
    user_cruds.create_user(db_session_override, UserCreate(name="User1", email="user1@example.com", phone_number=get_unique_phone_number(), password="StrongPass1!"))
    user_cruds.create_user(db_session_override, UserCreate(name="User2", email="user2@example.com", phone_number=get_unique_phone_number(), password="StrongPass2!"))
    user_cruds.create_user(db_session_override, UserCreate(name="User3", email="user3@example.com", phone_number=get_unique_phone_number(), password="StrongPass3!"))
    
    # Act: Get all users
    users = user_cruds.get_users(db_session_override)
    
    # Assert
    assert len(users) == 3
    assert {u.email for u in users} == {"user1@example.com", "user2@example.com", "user3@example.com"}

def test_get_users_with_skip_and_limit(db_session_override: Session):
    # Arrange: Create multiple users
    for i in range(1, 6):
        # Gerar telefone único e válido para cada usuário (13 dígitos)
        phone_num = f"5511987654{i:03d}" # Ex: 5511987654001, 5511987654002, etc. (13 dígitos)
        user_cruds.create_user(db_session_override, UserCreate(name=f"User{i}", email=f"user{i}@example.com", phone_number = phone_num, password=f"Pass{i}123!"))
    
    # Act: Get users with skip=1, limit=2
    users = user_cruds.get_users(db_session_override, skip=1, limit=2)
    
    # Assert
    assert len(users) == 2
    assert users[0].name == "User2"
    assert users[1].name == "User3"

# --- Tests for create_user ---

def test_create_user_success(db_session_override: Session):
    # Arrange
    user_data = UserCreate(
        name="New User",
        email="newuser@example.com",
        phone_number=get_unique_phone_number(), # Usar função auxiliar
        password="NewUserPass123!" # Senha forte
    )
    
    # Act
    created_user = user_cruds.create_user(db_session_override, user_data)
    
    # Assert
    assert created_user.id is not None
    assert created_user.name == "New User"
    assert created_user.email == "newuser@example.com"
    assert created_user.phone_number == user_data.phone_number # Assert no valor gerado
    assert created_user.creation_date is not None
    assert verify_password("NewUserPass123!", created_user.password_hash)
    
    # Verify in DB
    user_in_db = db_session_override.query(User).filter(User.id == created_user.id).first()
    assert user_in_db is not None
    assert user_in_db.email == "newuser@example.com"

def test_create_user_duplicate_email(db_session_override: Session):
    # Arrange: Create a user
    user_cruds.create_user(db_session_override, UserCreate(name="Existing", email="duplicate@example.com", phone_number=get_unique_phone_number(), password="Pass123!"))
    
    # Act & Assert: Try to create another user with the same email
    with pytest.raises(HTTPException) as exc_info: # Captura HTTPException
        user_cruds.create_user(db_session_override, UserCreate(name="Another", email="duplicate@example.com", phone_number=get_unique_phone_number(), password="Pass123!"))
    
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "Email já registrado por outro usuário."

def test_create_user_duplicate_phone_number(db_session_override: Session):
    # Arrange: Create a user with a specific phone number
    duplicate_phone = get_unique_phone_number()
    user_cruds.create_user(db_session_override, UserCreate(name="Existing", email="phone_dup@example.com", phone_number=duplicate_phone, password="Pass123!"))
    
    # Act & Assert: Try to create another user with the same phone number
    with pytest.raises(HTTPException) as exc_info: # Captura HTTPException
        user_cruds.create_user(db_session_override, UserCreate(name="Another", email="another_phone_dup@example.com", phone_number=duplicate_phone, password="Pass123!"))
    
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "Número de telefone já registrado por outro usuário."

# --- Tests for update_user ---

def test_update_user_success(db_session_override: Session):
    # Arrange: Create a user
    user_data = UserCreate(name="Original Name", email="update@example.com", phone_number=get_unique_phone_number(), password="Pass123!")
    db_user = user_cruds.create_user(db_session_override, user_data)
    
    # Act: Update user's name and phone number
    update_data = UserUpdate(name="Updated Name", phone_number=get_unique_phone_number()) # Novo telefone único
    updated_user = user_cruds.update_user(db_session_override, db_user.id, update_data)
    
    # Assert
    assert updated_user is not None
    assert updated_user.id == db_user.id
    assert updated_user.name == "Updated Name"
    assert updated_user.phone_number == update_data.phone_number # Assert no valor atualizado
    assert updated_user.email == db_user.email
    assert verify_password("Pass123!", updated_user.password_hash)
    
    # Verify in DB
    user_in_db = db_session_override.query(User).filter(User.id == db_user.id).first()
    assert user_in_db.name == "Updated Name"
    assert user_in_db.phone_number == update_data.phone_number

def test_update_user_change_password(db_session_override: Session):
    # Arrange: Create a user
    user_data = UserCreate(name="Pass123! User", email="Pass123!@example.com", phone_number=get_unique_phone_number(), password="Pass123!")
    db_user = user_cruds.create_user(db_session_override, user_data)
    
    # Act: Update user's password
    new_password = "NewStrongP@55word!" # Senha nova e forte, com caractere especial
    update_data = UserUpdate(password=new_password)
    updated_user = user_cruds.update_user(db_session_override, db_user.id, update_data)
    
    # Assert
    assert updated_user is not None
    assert verify_password(new_password, updated_user.password_hash)
    
    # Verify in DB
    user_in_db = db_session_override.query(User).filter(User.id == db_user.id).first()
    assert verify_password(new_password, user_in_db.password_hash)

def test_update_user_not_exists(db_session_override: Session):
    # Act: Try to update a non-existent user
    update_data = UserUpdate(name="Non Existent User", phone_number="999999999999") # Telefone válido para o schema
    updated_user = user_cruds.update_user(db_session_override, 99999, update_data)
    
    # Assert
    assert updated_user is None

def test_update_user_duplicate_email(db_session_override: Session):
    # Arrange: Create two users
    user1_data = UserCreate(name="User1", email="user1_update@example.com", phone_number=get_unique_phone_number(), password="Pass123!")
    user2_data = UserCreate(name="User2", email="user2_update@example.com", phone_number=get_unique_phone_number(), password="Pass123!")
    db_user1 = user_cruds.create_user(db_session_override, user1_data)
    user_cruds.create_user(db_session_override, user2_data)
    
    # Act & Assert: Try to update user1's email to user2's email
    update_data = UserUpdate(email="user2_update@example.com")
    with pytest.raises(HTTPException) as exc_info: # Captura HTTPException
        user_cruds.update_user(db_session_override, db_user1.id, update_data)
    
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "Email já registrado por outro usuário."

def test_update_user_duplicate_phone_number(db_session_override: Session):
    # Arrange: Create two users
    user1_data = UserCreate(name="User1", email="user1_phone_update@example.com", phone_number=get_unique_phone_number(), password="Pass123!")
    user2_data = UserCreate(name="User2", email="user2_phone_update@example.com", phone_number=get_unique_phone_number(), password="Pass123!")
    db_user1 = user_cruds.create_user(db_session_override, user1_data)
    user_cruds.create_user(db_session_override, user2_data)
    
    # Act & Assert: Try to update user1's phone number to user2's phone number
    update_data = UserUpdate(phone_number=user2_data.phone_number) # Usar o telefone do user2_data
    with pytest.raises(HTTPException) as exc_info: # Captura HTTPException
        user_cruds.update_user(db_session_override, db_user1.id, update_data)
    
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "Número de telefone já registrado por outro usuário."

def test_update_user_none_values(db_session_override: Session):
    # Arrange: Create a user with all fields populated
    user_data = UserCreate(name="Full User", email="full@example.com", phone_number=get_unique_phone_number(), password="Pass123!")
    db_user = user_cruds.create_user(db_session_override, user_data)
    
    # Act: Update with some fields set to None (but not unset)
    update_data = UserUpdate(name="Updated Name", email=None, phone_number=None) 
    updated_user = user_cruds.update_user(db_session_override, db_user.id, update_data)
    
    # Assert: Fields explicitly set to None should be updated to None in DB
    assert updated_user.name == "Updated Name"
    assert updated_user.email is None # Email deve ser None
    assert updated_user.phone_number is None # Phone_number deve ser None

    user_in_db = db_session_override.query(User).filter(User.id == db_user.id).first()
    assert user_in_db.name == "Updated Name"
    assert user_in_db.email is None
    assert user_in_db.phone_number is None


# --- Tests for delete_user ---

def test_delete_user_success(db_session_override: Session):
    # Arrange: Create a user to delete
    user_data = UserCreate(name="To Be Deleted", email="delete@example.com", phone_number=get_unique_phone_number(), password="Pass123!")
    db_user = user_cruds.create_user(db_session_override, user_data)
    
    # Act
    is_deleted = user_cruds.delete_user(db_session_override, db_user.id)
    
    # Assert
    assert is_deleted is True
    
    # Verify in DB
    user_in_db = db_session_override.query(User).filter(User.id == db_user.id).first()
    assert user_in_db is None

def test_delete_user_not_exists(db_session_override: Session):
    # Act: Try to delete a non-existent user
    is_deleted = user_cruds.delete_user(db_session_override, 99999)
    
    # Assert
    assert is_deleted is False

# --- Tests for get_user_by_identifier ---

def test_get_user_by_identifier_by_email(db_session_override: Session):
    # Arrange: Create a user
    user_data = UserCreate(name="ID User", email="id_email@example.com", phone_number=get_unique_phone_number(), password="Pass123!")
    user_cruds.create_user(db_session_override, user_data)
    
    # Act
    fetched_user = user_cruds.get_user_by_identifier(db_session_override, "id_email@example.com")
    
    # Assert
    assert fetched_user is not None
    assert fetched_user.email == "id_email@example.com"

def test_get_user_by_identifier_by_phone_number(db_session_override: Session):
    # Arrange: Create a user
    phone_num = get_unique_phone_number()
    user_data = UserCreate(name="ID User", email="id_phone@example.com", phone_number=phone_num, password="Pass123!")
    user_cruds.create_user(db_session_override, user_data)
    
    # Act
    fetched_user = user_cruds.get_user_by_identifier(db_session_override, phone_num)
    
    # Assert
    assert fetched_user is not None
    assert fetched_user.phone_number == phone_num

def test_get_user_by_identifier_not_found(db_session_override: Session):
    # Act
    fetched_user = user_cruds.get_user_by_identifier(db_session_override, "nonexistent@example.com")
    assert fetched_user is None
    fetched_user = user_cruds.get_user_by_identifier(db_session_override, "999999999999") # Telefone válido para o schema, mas não existe
    assert fetched_user is None

# --- Tests for verify_user_password ---

def test_verify_user_password_correct(db_session_override: Session):
    # Arrange: Create a user with a known password
    user_data = UserCreate(name="Verify User", email="verify@example.com", phone_number=get_unique_phone_number(), password="C0rr3ctP@55w0rd!") # Senha forte
    db_user = user_cruds.create_user(db_session_override, user_data)
    
    # Act
    is_correct = user_cruds.verify_user_password(db_session_override, db_user.id, "C0rr3ctP@55w0rd!")
    
    # Assert
    assert is_correct is True

def test_verify_user_password_incorrect(db_session_override: Session):
    # Arrange: Create a user
    user_data = UserCreate(name="Verify User", email="verify_fail@example.com", phone_number=get_unique_phone_number(), password="C0rr3ctP@55w0rd!") # Senha forte
    db_user = user_cruds.create_user(db_session_override, user_data)
    
    # Act
    is_correct = user_cruds.verify_user_password(db_session_override, db_user.id, "wrong_password")
    
    # Assert
    assert is_correct is False

def test_verify_user_password_user_not_found(db_session_override: Session):
    # Act
    is_correct = user_cruds.verify_user_password(db_session_override, 99999, "any_password")
    
    # Assert
    assert is_correct is False
