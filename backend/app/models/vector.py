from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class ResumeChunk(Base):
    __tablename__ = "resume_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("candidate_resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)

    # Chunk Info
    chunk_text = Column(Text, nullable=False)
    chunk_order = Column(Integer, nullable=False)  # Order in the document
    chunk_type = Column(String(100), index=True)  # summary, skills, experience, education, etc.

    # Metadata
    chunk_metadata = Column(JSONB)  # Additional context about the chunk

    # Character positions
    start_char = Column(Integer)
    end_char = Column(Integer)

    # Embedding info
    embedding_model = Column(String(200))  # Model used for embedding
    is_embedded = Column(Boolean, default=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    resume = relationship("CandidateResume", back_populates="chunks")
    embedding = relationship("ChunkEmbedding", back_populates="chunk", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_chunk_resume_order', 'resume_id', 'chunk_order'),
        Index('idx_chunk_type', 'chunk_type', 'is_embedded'),
    )


class ChunkEmbedding(Base):
    __tablename__ = "chunk_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("resume_chunks.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Embedding Vector (stored as JSONB for PostgreSQL compatibility)
    # In production, consider using pgvector extension for native vector support
    embedding_vector = Column(JSONB, nullable=False)  # Array of floats
    embedding_dimension = Column(Integer, nullable=False)

    # FAISS Index Info
    faiss_index_id = Column(Integer)  # Position in FAISS index
    faiss_index_version = Column(String(50))  # Which version of the index

    # Model Info
    model_name = Column(String(200), nullable=False)
    model_version = Column(String(100))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    chunk = relationship("ResumeChunk", back_populates="embedding")


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Query Info
    query_text = Column(Text, nullable=False)
    query_type = Column(String(50), index=True)  # semantic, hybrid, keyword

    # Filters
    filters = Column(JSONB)  # Location, experience, skills, etc.

    # Results
    total_results = Column(Integer)
    top_score = Column(Float)

    # Performance
    execution_time_ms = Column(Integer)

    # User Context
    user_id = Column(String(200))
    session_id = Column(String(200))

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    results = relationship("SearchResult", back_populates="query", cascade="all, delete-orphan")


class SearchResult(Base):
    __tablename__ = "search_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("search_queries.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)

    # Ranking
    rank = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)

    # Score Components
    semantic_score = Column(Float)
    keyword_score = Column(Float)
    rerank_score = Column(Float)

    # Matched Chunks
    matched_chunk_ids = Column(ARRAY(UUID(as_uuid=True)))  # Array of chunk IDs that matched

    # Interaction
    clicked = Column(Boolean, default=False)
    clicked_at = Column(DateTime(timezone=True))

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    query = relationship("SearchQuery", back_populates="results")


class DuplicateCandidate(Base):
    __tablename__ = "duplicate_candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Candidates
    candidate_1_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_2_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)

    # Similarity Scores
    overall_similarity_score = Column(Float, nullable=False, index=True)  # 0-100
    email_match = Column(Boolean, default=False)
    phone_match = Column(Boolean, default=False)
    name_similarity = Column(Float)  # Levenshtein distance
    resume_similarity = Column(Float)  # Based on embeddings
    employment_overlap = Column(Float)  # Percentage of overlapping employment history

    # Detection Method
    detection_method = Column(String(100))  # exact_email, fuzzy_name, semantic, employment

    # Status
    status = Column(String(50), default="pending", index=True)  # pending, confirmed, dismissed, merged
    reviewed_by = Column(String(200))
    reviewed_at = Column(DateTime(timezone=True))

    # Merge Info
    merged_into_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="SET NULL"))
    merged_at = Column(DateTime(timezone=True))

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_duplicate_score', 'overall_similarity_score', 'status'),
        Index('idx_duplicate_candidates', 'candidate_1_id', 'candidate_2_id'),
    )


class SystemMetrics(Base):
    __tablename__ = "system_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Metric Info
    metric_name = Column(String(200), nullable=False, index=True)
    metric_category = Column(String(100), index=True)  # embedding, search, application, system
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50))  # seconds, count, percentage, etc.

    # Context
    context = Column(JSONB)  # Additional context about the metric

    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        Index('idx_metrics_time', 'metric_name', 'recorded_at'),
        Index('idx_metrics_category', 'metric_category', 'recorded_at'),
    )
