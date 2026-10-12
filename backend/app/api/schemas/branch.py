"""Branch API Schemas"""

from datetime import datetime
from pydantic import BaseModel, Field


class BranchCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=255)
    address: str | None = Field(None, max_length=500)
    phone: str | None = Field(None, max_length=20)
    description: str | None = None


class BranchUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    location: str | None = Field(None, min_length=1, max_length=255)
    address: str | None = None
    phone: str | None = None
    description: str | None = None


class BranchResponse(BaseModel):
    id: str
    name: str
    location: str
    address: str | None
    phone: str | None
    description: str | None
    is_active: bool
    coordinator_id: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BranchStatisticsResponse(BaseModel):
    branch: BranchResponse
    youth_count: int
    department_count: int
    attendance_rate: float


class CoordinatorAssignmentRequest(BaseModel):
    coordinator_id: str = Field(..., description="User ID with BRANCH_COORDINATOR role")
