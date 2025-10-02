# Import all models here so Alembic can detect them
from app.models.user import User, UserRole

from app.models.candidate import (
    Candidate,
    CandidateResume,
    CandidateSkill,
    CandidateExperience,
    CandidateEducation,
    CandidateCertification,
    CandidateReference
)

from app.models.job import (
    Job,
    Application,
    ApplicationStatusHistory,
    Interview,
    JobRecommendation
)

from app.models.integration import (
    LinkedInProfile,
    GitHubProfile,
    GitHubRepository,
    StackOverflowProfile,
    MediumProfile,
    ArticleBlog,
    YouTubeProfile,
    YouTubeVideo,
    IntegrationSyncLog
)

from app.models.vector import (
    ResumeChunk,
    ChunkEmbedding,
    SearchQuery,
    SearchResult,
    DuplicateCandidate,
    SystemMetrics
)

__all__ = [
    # Users (1 table)
    "User",
    "UserRole",

    # Candidates (7 tables)
    "Candidate",
    "CandidateResume",
    "CandidateSkill",
    "CandidateExperience",
    "CandidateEducation",
    "CandidateCertification",
    "CandidateReference",

    # Jobs (5 tables)
    "Job",
    "Application",
    "ApplicationStatusHistory",
    "Interview",
    "JobRecommendation",

    # Integrations (9 tables)
    "LinkedInProfile",
    "GitHubProfile",
    "GitHubRepository",
    "StackOverflowProfile",
    "MediumProfile",
    "ArticleBlog",
    "YouTubeProfile",
    "YouTubeVideo",
    "IntegrationSyncLog",

    # Vectors & Analytics (6 tables)
    "ResumeChunk",
    "ChunkEmbedding",
    "SearchQuery",
    "SearchResult",
    "DuplicateCandidate",
    "SystemMetrics",
]
