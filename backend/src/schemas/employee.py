# File: backend/src/schemas/employee.py

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class EmployeeBase(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=255)
    phone_number: str = Field(..., max_length=20)
    role: str = Field(..., max_length=50) # e.g., "Developer", "Designer", "Project Manager"
    is_active: bool = True

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=3, max_length=100)
    email: EmailStr | None = Field(None, max_length=255)
    password: str | None = Field(None, min_length=8, max_length=255)
    phone_number: str | None = Field(None, max_length=20)
    role: str | None = Field(None, max_length=50)
    is_active: bool | None = None

class EmployeeInDB(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True