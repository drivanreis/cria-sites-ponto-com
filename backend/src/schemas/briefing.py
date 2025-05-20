# File: backend/src/schemas/briefing.py

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class BriefingBase(BaseModel):
    user_id: int
    project_name: str = Field(..., min_length=3, max_length=255)
    project_description: str = Field(..., min_length=10)
    target_audience: str = Field(None, max_length=255)
    goals: str = Field(None, max_length=500)
    content_pages: str = Field(None, max_length=500) # e.g., "Home, About, Services, Contact"
    design_preferences: str = Field(None, max_length=500)
    technical_requirements: str = Field(None, max_length=500)
    status: str = Field("pending", max_length=50) # e.g., "pending", "in_progress", "completed", "cancelled"
    # Note: conversation_history will be handled separately as it's a relationship

class BriefingCreate(BriefingBase):
    pass

class BriefingUpdate(BaseModel):
    project_name: str | None = Field(None, min_length=3, max_length=255)
    project_description: str | None = Field(None, min_length=10)
    target_audience: str | None = Field(None, max_length=255)
    goals: str | None = Field(None, max_length=500)
    content_pages: str | None = Field(None, max_length=500)
    design_preferences: str | None = Field(None, max_length=500)
    technical_requirements: str | None = Field(None, max_length=500)
    status: str | None = Field(None, max_length=50)

class BriefingInDB(BriefingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True