import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.cruds import user_cruds 
from src.schemas.user_schemas import UserCreate, UserUpdate


_phone_number_counter = 0
def get_unique_phone_number() -> str:
    global _phone_number_counter
    _phone_number_counter += 1
    # Formato com 13 dígitos para se adequar à nova validação (12 a 14 números)
    # Ex: 5511987654321, 5511987654322, etc.
    return f"5511987654{_phone_number_counter:03d}" 

# --- Tests for get_user ---

# --- Tests for verify_user_email ---
def test_verify_user_email_verified(db_session_override: Session):
    # Arrange: Create a user not email verified
    user_data = UserCreate(
        name="User Not Verified",
        email="not_verified@example.com",
        phone_number=get_unique_phone_number(),
        password="VerifyUserPass1!" # Senha forte
    )
    created_user = user_cruds.create_user(db_session_override, user_data)
    assert created_user.email_verified == False # Deve ser False por padrão

    # Act: Verify the user's email
    updated_user = user_cruds.verify_user_email(db_session_override, created_user.id)

    # Assert: User's email_verified status is True
    assert updated_user is not None
    assert updated_user.id == created_user.id
    assert updated_user.email_verified == True

def test_verify_non_existent_user(db_session_override: Session):
    # Act & Assert: Attempt to verify a non-existent user
    updated_user = user_cruds.verify_user_email(db_session_override, 99999)
    assert updated_user is None # Assume que o CRUD retorna None para não encontrado, ou HTTPException se implementado


# --- Tests for block_user ---
def test_block_user(db_session_override: Session):
    # Arrange: Create a user
    user_data = UserCreate(
        name="User to Block",
        email="block_me@example.com",
        phone_number=get_unique_phone_number(),
        password="BlockUserPass1!" # Senha forte
    )
    created_user = user_cruds.create_user(db_session_override, user_data)
    assert created_user.status == "active" # Deve ser 'active' por padrão

    # Act: Block the user
    updated_user = user_cruds.block_user(db_session_override, created_user.id)

    # Assert: User status is 'blocked'
    assert updated_user is not None
    assert updated_user.id == created_user.id
    assert updated_user.status == "blocked"

def test_block_non_existent_user(db_session_override: Session):
    # Act & Assert: Attempt to block a non-existent user
    updated_user = user_cruds.block_user(db_session_override, 99999)
    assert updated_user is None # Assume que o CRUD retorna None para não encontrado, ou HTTPException se implementado

# --- Tests for unblock_user ---
def test_unblock_user(db_session_override: Session):
    # Arrange: Create a user and block him
    user_data = UserCreate(
        name="User to Unblock",
        email="unblock_me@example.com",
        phone_number=get_unique_phone_number(),
        password="UnblockUserPass1!" # Senha forte
    )
    created_user = user_cruds.create_user(db_session_override, user_data)
    user_cruds.block_user(db_session_override, created_user.id) # Bloqueia primeiro
    assert created_user.status == "blocked"

    # Act: Unblock the user
    updated_user = user_cruds.unblock_user(db_session_override, created_user.id)

    # Assert: User status is 'active'
    assert updated_user is not None
    assert updated_user.id == created_user.id
    assert updated_user.status == "active"

def test_unblock_non_existent_user(db_session_override: Session):
    # Act & Assert: Attempt to unblock a non-existent user
    updated_user = user_cruds.unblock_user(db_session_override, 99999)
    assert updated_user is None # Assume que o CRUD retorna None para não encontrado, ou HTTPException se implementado

# --- Tests for soft_delete_user ---
def test_soft_delete_user(db_session_override: Session):
    # Arrange: Create a user
    user_data = UserCreate(
        name="User to Soft Delete",
        email="soft_delete@example.com",
        phone_number=get_unique_phone_number(),
        password="SoftDeletePass1!" # Senha forte
    )
    created_user = user_cruds.create_user(db_session_override, user_data)
    assert created_user.status == "active"

    # Act: Soft delete the user
    updated_user = user_cruds.soft_delete_user(db_session_override, created_user.id)

    # Assert: User status is 'deleted'
    assert updated_user is not None
    assert updated_user.id == created_user.id
    assert updated_user.status == "deleted"

def test_soft_delete_non_existent_user(db_session_override: Session):
    # Act & Assert: Attempt to soft delete a non-existent user
    updated_user = user_cruds.soft_delete_user(db_session_override, 99999)
    assert updated_user is None # Assume que o CRUD retorna None para não encontrado, ou HTTPException se implementado

# --- Tests for soft_delete_user and recreate ---
def test_recreate_soft_deleted_user_with_new_credentials(db_session_override: Session):
    # Arrange: Create a user, soft delete it
    initial_email = "soft_deleted_recreate@example.com"
    initial_phone = get_unique_phone_number()
    user_data = UserCreate(name="Soft Deleted User", email=initial_email, phone_number=initial_phone, password="SoftDelPass1!")
    created_user = user_cruds.create_user(db_session_override, user_data)
    user_cruds.soft_delete_user(db_session_override, created_user.id)
    
    # Act: Attempt to create a new user with entirely new credentials (email and phone)
    new_user_data = UserCreate(
        name="Recreated User",
        email="recreated_new@example.com",
        phone_number=get_unique_phone_number(),
        password="RecreatePass1!"
    )
    recreated_user = user_cruds.create_user(db_session_override, new_user_data)

    # Assert: New user is created successfully
    assert recreated_user is not None
    assert recreated_user.id != created_user.id
    assert recreated_user.email == new_user_data.email
    assert recreated_user.phone_number == new_user_data.phone_number
    assert recreated_user.status == "active"

def test_recreate_soft_deleted_user_with_duplicate_credentials(db_session_override: Session):
    # Arrange: Create a user, soft delete it
    initial_email = "soft_deleted_duplicate@example.com"
    initial_phone = get_unique_phone_number()
    user_data = UserCreate(name="Soft Deleted User Dup", email=initial_email, phone_number=initial_phone, password="SoftDelDupPass1!")
    created_user = user_cruds.create_user(db_session_override, user_data)
    user_cruds.soft_delete_user(db_session_override, created_user.id)
    
    # Act & Assert: Attempt to create a new user with the SAME email (should fail)
    duplicate_email_data = UserCreate(
        name="Recreated User Dup Email",
        email=initial_email,
        phone_number=get_unique_phone_number(), # Deve ser único para o novo usuário
        password="RecreateDupPass1!"
    )
    with pytest.raises(HTTPException) as exc_info: # Captura HTTPException
        user_cruds.create_user(db_session_override, duplicate_email_data)
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "Email já registrado por outro usuário."

    # Act & Assert: Attempt to create a new user with the SAME phone number (should fail)
    duplicate_phone_data = UserCreate(
        name="Recreated User Dup Phone",
        email="another_new_email@example.com",
        phone_number=initial_phone, # Telefone duplicado
        password="RecreateDupPass2!"
    )
    with pytest.raises(HTTPException) as exc_info: # Captura HTTPException
        user_cruds.create_user(db_session_override, duplicate_phone_data)
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "Número de telefone já registrado por outro usuário."