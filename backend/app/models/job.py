from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic Info
    title = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=False)
    department = Column(String(200), index=True)
    location = Column(String(255), index=True)

    # Employment Details
    employment_type = Column(String(50), index=True)  # full-time, part-time, contract, internship
    work_mode = Column(String(50))  # remote, hybrid, onsite

    # Salary
    salary_min = Column(Float)
    salary_max = Column(Float)
    currency = Column(String(3), default="USD")

    # Requirements
    required_skills = Column(ARRAY(String))
    preferred_skills = Column(ARRAY(String))
    experience_min = Column(Integer, index=True)
    experience_max = Column(Integer)
    education_level = Column(String(100))  # High School, Bachelor's, Master's, PhD

    # Job Details
    responsibilities = Column(JSONB)  # Array of responsibilities
    benefits = Column(JSONB)  # Array of benefits

    # Status
    status = Column(String(50), default="draft", index=True)  # draft, active, closed, on_hold
    priority = Column(String(20), default="medium")  # low, medium, high, urgent

    # Metadata
    posted_by = Column(String(200))  # recruiter/hiring manager name or ID
    number_of_openings = Column(Integer, default=1)
    application_deadline = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    posted_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))

    # Relationships
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    recommendations = relationship("JobRecommendation", back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_job_search', 'title', 'location', 'status'),
        Index('idx_job_experience', 'experience_min', 'experience_max'),
    )


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # References
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("candidate_resumes.id", ondelete="SET NULL"))

    # Application Info
    status = Column(String(50), default="submitted", nullable=False, index=True)
    # Status flow: submitted → under_review → shortlisted → interview_scheduled →
    #              interview_completed → offer_extended → offer_accepted/rejected → hired/rejected

    cover_letter = Column(Text)

    # Scoring
    match_score = Column(Float)  # Overall match score (0-100)
    skill_match_score = Column(Float)
    experience_match_score = Column(Float)
    location_match_score = Column(Float)

    # Match Explanation
    match_explanation = Column(Text)

    # Metadata
    source = Column(String(100))  # direct, referral, job_board, etc.
    notes = Column(Text)

    # Timestamps
    applied_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reviewed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    status_history = relationship("ApplicationStatusHistory", back_populates="application", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_application_status', 'job_id', 'status'),
        Index('idx_application_score', 'job_id', 'match_score'),
    )


class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)

    from_status = Column(String(50))
    to_status = Column(String(50), nullable=False)
    notes = Column(Text)
    changed_by = Column(String(200))  # recruiter name or ID

    # Timestamp
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    application = relationship("Application", back_populates="status_history")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)

    # Interview Details
    interview_type = Column(String(100))  # phone, video, onsite, technical, hr, final
    round = Column(Integer, default=1)
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer, default=60)

    # Location/Link
    location = Column(String(500))  # physical address or video call link
    meeting_notes = Column(Text)

    # Interviewer
    interviewer_name = Column(String(200))
    interviewer_email = Column(String(255))

    # Status
    status = Column(String(50), default="scheduled")  # scheduled, completed, cancelled, rescheduled

    # Feedback
    feedback = Column(Text)
    rating = Column(Integer)  # 1-5 or 1-10
    recommendation = Column(String(50))  # strong_yes, yes, maybe, no, strong_no

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    application = relationship("Application", back_populates="interviews")


class JobRecommendation(Base):
    __tablename__ = "job_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # References
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)

    # Scoring
    overall_score = Column(Float, nullable=False, index=True)  # 0-100
    semantic_similarity_score = Column(Float)
    skill_match_score = Column(Float)
    experience_match_score = Column(Float)
    location_match_score = Column(Float)

    # Explanation
    explanation = Column(Text)
    matched_skills = Column(ARRAY(String))
    missing_skills = Column(ARRAY(String))

    # Metadata
    recommendation_reason = Column(Text)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    job = relationship("Job", back_populates="recommendations")

    __table_args__ = (
        Index('idx_recommendation_score', 'job_id', 'overall_score'),
    )
