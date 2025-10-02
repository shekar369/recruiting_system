from app.schemas.candidate import (
    CandidateBase,
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateListResponse,
    SkillBase,
    SkillCreate,
    SkillResponse,
    ResumeBase,
    ResumeResponse,
)

from app.schemas.job import (
    JobBase,
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse,
    ApplicationBase,
    ApplicationCreate,
    ApplicationResponse,
)

__all__ = [
    # Candidate schemas
    "CandidateBase",
    "CandidateCreate",
    "CandidateUpdate",
    "CandidateResponse",
    "CandidateListResponse",
    "SkillBase",
    "SkillCreate",
    "SkillResponse",
    "ResumeBase",
    "ResumeResponse",

    # Job schemas
    "JobBase",
    "JobCreate",
    "JobUpdate",
    "JobResponse",
    "JobListResponse",
    "ApplicationBase",
    "ApplicationCreate",
    "ApplicationResponse",
]
