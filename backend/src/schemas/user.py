# File: backend/src/schemas/user.py

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=255)
    phone_number: str = Field(..., max_length=20)
    company_name: str = Field(None, max_length=100)
    role: str = Field("client", max_length=50) # Default role for a user
    is_active: bool = True

class UserCreate(UserBase):
    # Password will be hashed before storing, so we keep it here for creation
    pass

class UserUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=3, max_length=100)
    email: EmailStr | None = Field(None, max_length=255)
    password: str | None = Field(None, min_length=8, max_length=255)
    phone_number: str | None = Field(None, max_length=20)
    company_name: str | None = Field(None, max_length=100)
    role: str | None = Field(None, max_length=50)
    is_active: bool | None = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True # Enables ORM mode for Pydantic to read ORM objects