from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    location = Column(String(255), index=True)

    # Professional Info
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    portfolio_url = Column(String(500))
    years_of_experience = Column(Integer, index=True)
    current_job_title = Column(String(200), index=True)
    current_company = Column(String(200))

    # Salary Expectations
    expected_salary_min = Column(Float)
    expected_salary_max = Column(Float)
    currency = Column(String(3), default="USD")

    # Availability
    availability = Column(String(50))  # immediate, 2weeks, 1month, etc.

    # Status
    status = Column(String(50), default="active", index=True)  # active, inactive, hired, blacklisted

    # Metadata
    source = Column(String(100))  # linkedin, referral, job_board, etc.
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    resumes = relationship("CandidateResume", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    experience = relationship("CandidateExperience", back_populates="candidate", cascade="all, delete-orphan")
    education = relationship("CandidateEducation", back_populates="candidate", cascade="all, delete-orphan")
    certifications = relationship("CandidateCertification", back_populates="candidate", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="candidate", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_candidate_name', 'first_name', 'last_name'),
        Index('idx_candidate_location_exp', 'location', 'years_of_experience'),
    )


class CandidateResume(Base):
    __tablename__ = "candidate_resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)

    # File Info
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(50))  # pdf, docx
    file_size = Column(Integer)

    # Parsed Data
    raw_text = Column(Text)
    parsed_data = Column(JSONB)  # Structured extracted data

    # Processing Status
    is_processed = Column(Boolean, default=False)
    is_chunked = Column(Boolean, default=False)
    is_embedded = Column(Boolean, default=False)

    # Metadata
    is_primary = Column(Boolean, default=False)
    version = Column(Integer, default=1)

    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True))

    # Relationships
    candidate = relationship("Candidate", back_populates="resumes")
    chunks = relationship("ResumeChunk", back_populates="resume", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_resume_processing', 'candidate_id', 'is_processed'),
    )


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)

    skill_name = Column(String(200), nullable=False, index=True)
    skill_category = Column(String(100), index=True)  # programming, framework, tool, soft_skill, etc.
    proficiency_level = Column(String(50))  # beginner, intermediate, advanced, expert
    years_of_experience = Column(Integer)

    # Source
    source = Column(String(100))  # resume, linkedin, github, manual
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    candidate = relationship("Candidate", back_populates="skills")

    __table_args__ = (
        Index('idx_skill_search', 'skill_name', 'proficiency_level'),
    )


class CandidateExperience(Base):
    __tablename__ = "candidate_experience"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)

    company_name = Column(String(200), nullable=False)
    job_title = Column(String(200), nullable=False)
    location = Column(String(255))

    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    is_current = Column(Boolean, default=False)

    description = Column(Text)
    responsibilities = Column(JSONB)  # Array of responsibilities
    achievements = Column(JSONB)  # Array of achievements

    # Source
    source = Column(String(100))  # resume, linkedin, manual

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    candidate = relationship("Candidate", back_populates="experience")

    __table_args__ = (
        Index('idx_experience_company', 'company_name', 'job_title'),
    )


class CandidateEducation(Base):
    __tablename__ = "candidate_education"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)

    institution_name = Column(String(300), nullable=False)
    degree = Column(String(200))  # Bachelor's, Master's, PhD, etc.
    field_of_study = Column(String(200))

    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    is_current = Column(Boolean, default=False)

    grade = Column(String(50))  # GPA, percentage, etc.
    description = Column(Text)

    # Source
    source = Column(String(100))  # resume, linkedin, manual

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    candidate = relationship("Candidate", back_populates="education")


class CandidateCertification(Base):
    __tablename__ = "candidate_certifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)

    certification_name = Column(String(300), nullable=False)
    issuing_organization = Column(String(300))
    issue_date = Column(DateTime(timezone=True))
    expiry_date = Column(DateTime(timezone=True))
    credential_id = Column(String(200))
    credential_url = Column(String(500))

    # Source
    source = Column(String(100))  # resume, linkedin, manual

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    candidate = relationship("Candidate", back_populates="certifications")


class CandidateReference(Base):
    __tablename__ = "candidate_references"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(200), nullable=False)
    relationship = Column(String(100))  # manager, colleague, mentor, etc.
    company = Column(String(200))
    job_title = Column(String(200))
    email = Column(String(255))
    phone = Column(String(20))

    notes = Column(Text)
    is_contacted = Column(Boolean, default=False)
    contact_date = Column(DateTime(timezone=True))
    feedback = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
