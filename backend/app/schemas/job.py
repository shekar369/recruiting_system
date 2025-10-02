from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# Base schemas
class JobBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    department: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=255)

    # Employment Details
    employment_type: Optional[str] = Field(None, max_length=50)  # full-time, part-time, contract, internship
    work_mode: Optional[str] = Field(None, max_length=50)  # remote, hybrid, onsite

    # Salary
    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field("USD", max_length=3)

    # Requirements
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    experience_min: Optional[int] = Field(None, ge=0, le=50)
    experience_max: Optional[int] = Field(None, ge=0, le=50)
    education_level: Optional[str] = Field(None, max_length=100)

    # Job Details
    responsibilities: Optional[dict] = None
    benefits: Optional[dict] = None

    # Status
    status: Optional[str] = Field("draft", max_length=50)  # draft, active, closed, on_hold
    priority: Optional[str] = Field("medium", max_length=20)  # low, medium, high, urgent

    # Metadata
    posted_by: Optional[str] = Field(None, max_length=200)
    number_of_openings: Optional[int] = Field(1, ge=1)
    application_deadline: Optional[datetime] = None


class JobCreate(JobBase):
    """Schema for creating a new job"""
    pass


class JobUpdate(BaseModel):
    """Schema for updating a job - all fields optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = Field(None, min_length=1)
    department: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=255)
    employment_type: Optional[str] = Field(None, max_length=50)
    work_mode: Optional[str] = Field(None, max_length=50)
    salary_min: Optional[float] = Field(None, ge=0)
    salary_max: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    experience_min: Optional[int] = Field(None, ge=0, le=50)
    experience_max: Optional[int] = Field(None, ge=0, le=50)
    education_level: Optional[str] = Field(None, max_length=100)
    responsibilities: Optional[dict] = None
    benefits: Optional[dict] = None
    status: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field(None, max_length=20)
    posted_by: Optional[str] = Field(None, max_length=200)
    number_of_openings: Optional[int] = Field(None, ge=1)
    application_deadline: Optional[datetime] = None


class JobResponse(JobBase):
    """Schema for job response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    posted_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    """Schema for paginated job list"""
    total: int
    page: int
    size: int
    jobs: List[JobResponse]


# Application schemas
class ApplicationBase(BaseModel):
    candidate_id: UUID
    job_id: UUID
    resume_id: Optional[UUID] = None
    cover_letter: Optional[str] = None
    source: Optional[str] = Field(None, max_length=100)


class ApplicationCreate(ApplicationBase):
    """Schema for creating an application"""
    pass


class ApplicationResponse(ApplicationBase):
    id: UUID
    status: str
    match_score: Optional[float] = None
    skill_match_score: Optional[float] = None
    experience_match_score: Optional[float] = None
    location_match_score: Optional[float] = None
    match_explanation: Optional[str] = None
    notes: Optional[str] = None
    applied_at: datetime
    reviewed_at: Optional[datetime] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
