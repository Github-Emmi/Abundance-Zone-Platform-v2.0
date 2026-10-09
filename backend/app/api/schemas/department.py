"""Department API Schemas"""
from datetime import datetime
from pydantic import BaseModel, Field


class DepartmentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    branch_id: str
    description: str | None = None


class DepartmentUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None


class DepartmentResponse(BaseModel):
    id: str
    name: str
    branch_id: str
    leader_id: str | None
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeaderAssignmentRequest(BaseModel):
    leader_id: str = Field(..., description="User ID with DEPARTMENT_LEADER role")


class MemberManagementRequest(BaseModel):
    user_ids: list[str] = Field(..., min_items=1)


class ScheduleUpdateRequest(BaseModel):
    schedule: dict = Field(..., description="Recurring schedule data")
