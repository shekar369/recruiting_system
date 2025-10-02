from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# Base schemas
class CandidateBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=255)

    # Professional Info
    linkedin_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    years_of_experience: Optional[int] = Field(None, ge=0, le=70)
    current_job_title: Optional[str] = Field(None, max_length=200)
    current_company: Optional[str] = Field(None, max_length=200)

    # Salary Expectations
    expected_salary_min: Optional[float] = Field(None, ge=0)
    expected_salary_max: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field("USD", max_length=3)

    # Availability
    availability: Optional[str] = Field(None, max_length=50)

    # Status
    status: Optional[str] = Field("active", max_length=50)

    # Metadata
    source: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class CandidateCreate(CandidateBase):
    """Schema for creating a new candidate"""
    pass


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate - all fields optional"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=255)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    years_of_experience: Optional[int] = Field(None, ge=0, le=70)
    current_job_title: Optional[str] = Field(None, max_length=200)
    current_company: Optional[str] = Field(None, max_length=200)
    expected_salary_min: Optional[float] = Field(None, ge=0)
    expected_salary_max: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    availability: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class CandidateResponse(CandidateBase):
    """Schema for candidate response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateListResponse(BaseModel):
    """Schema for paginated candidate list"""
    total: int
    page: int
    size: int
    candidates: List[CandidateResponse]


# Skill schemas
class SkillBase(BaseModel):
    skill_name: str = Field(..., max_length=200)
    skill_category: Optional[str] = Field(None, max_length=100)
    proficiency_level: Optional[str] = Field(None, max_length=50)
    years_of_experience: Optional[int] = Field(None, ge=0)


class SkillCreate(SkillBase):
    candidate_id: UUID


class SkillResponse(SkillBase):
    id: UUID
    candidate_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Resume schemas
class ResumeBase(BaseModel):
    file_name: str
    file_type: Optional[str] = None
    is_primary: Optional[bool] = False


class ResumeResponse(ResumeBase):
    id: UUID
    candidate_id: UUID
    file_path: str
    file_size: Optional[int] = None
    is_processed: bool
    is_chunked: bool
    is_embedded: bool
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
