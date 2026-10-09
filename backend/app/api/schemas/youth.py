"""Youth API Schemas"""
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from app.domain.value_objects.enums import Gender


class YouthCreateRequest(BaseModel):
    fullname: str = Field(..., min_length=1, max_length=150)
    branch_id: str
    gender: Gender
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    department_id: str | None = None
    date_of_birth: datetime | None = None


class YouthUpdateRequest(BaseModel):
    fullname: str | None = Field(None, min_length=1, max_length=150)
    email: EmailStr | None = None
    phone: str | None = None
    department_id: str | None = None


class YouthResponse(BaseModel):
    id: str
    fullname: str
    branch_id: str
    gender: str
    email: str | None
    phone: str | None
    department_id: str | None
    membership_status: str
    attendance_rate: float
    profile_image_url: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True


class YouthSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    branch_id: str | None = None
