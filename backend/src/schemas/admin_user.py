# File: backend/src/schemas/admin_user.py

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class AdminUserBase(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=255)
    is_active: bool = True
    is_super_admin: bool = False

class AdminUserCreate(AdminUserBase):
    pass

class AdminUserUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=3, max_length=100)
    email: EmailStr | None = Field(None, max_length=255)
    password: str | None = Field(None, min_length=8, max_length=255)
    is_active: bool | None = None
    is_super_admin: bool | None = None

class AdminUserInDB(AdminUserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True