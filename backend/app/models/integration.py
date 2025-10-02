from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class LinkedInProfile(Base):
    __tablename__ = "linkedin_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # LinkedIn Info
    linkedin_id = Column(String(200), unique=True)
    profile_url = Column(String(500), nullable=False)

    # Profile Data
    headline = Column(String(500))
    summary = Column(Text)
    profile_picture_url = Column(String(500))

    # Connection Info
    connections_count = Column(Integer)
    followers_count = Column(Integer)

    # Raw Data
    raw_data = Column(JSONB)  # Complete profile data from LinkedIn API

    # OAuth
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime(timezone=True))

    # Sync Info
    last_synced_at = Column(DateTime(timezone=True))
    sync_status = Column(String(50), default="pending")  # pending, syncing, completed, failed
    sync_error = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class GitHubProfile(Base):
    __tablename__ = "github_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # GitHub Info
    github_id = Column(String(200), unique=True)
    username = Column(String(200), nullable=False, unique=True)
    profile_url = Column(String(500), nullable=False)

    # Profile Data
    name = Column(String(200))
    bio = Column(Text)
    avatar_url = Column(String(500))
    location = Column(String(255))
    company = Column(String(200))
    blog = Column(String(500))

    # Stats
    public_repos = Column(Integer)
    public_gists = Column(Integer)
    followers = Column(Integer)
    following = Column(Integer)

    # Raw Data
    raw_data = Column(JSONB)

    # OAuth
    access_token = Column(Text)
    token_expires_at = Column(DateTime(timezone=True))

    # Sync Info
    last_synced_at = Column(DateTime(timezone=True))
    sync_status = Column(String(50), default="pending")
    sync_error = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    repositories = relationship("GitHubRepository", back_populates="profile", cascade="all, delete-orphan")


class GitHubRepository(Base):
    __tablename__ = "github_repositories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github_profile_id = Column(UUID(as_uuid=True), ForeignKey("github_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Repo Info
    repo_id = Column(String(200), unique=True)
    name = Column(String(300), nullable=False)
    full_name = Column(String(500))
    description = Column(Text)
    url = Column(String(500))

    # Stats
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    watchers = Column(Integer, default=0)
    open_issues = Column(Integer, default=0)

    # Technical Details
    primary_language = Column(String(100), index=True)
    languages = Column(JSONB)  # {language: bytes_of_code}
    topics = Column(JSONB)  # Array of topics/tags

    # Metadata
    is_fork = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)
    created_at_github = Column(DateTime(timezone=True))
    updated_at_github = Column(DateTime(timezone=True))
    pushed_at_github = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    profile = relationship("GitHubProfile", back_populates="repositories")


class StackOverflowProfile(Base):
    __tablename__ = "stackoverflow_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # StackOverflow Info
    user_id = Column(String(200), unique=True)
    profile_url = Column(String(500), nullable=False)
    display_name = Column(String(200))

    # Stats
    reputation = Column(Integer, default=0, index=True)
    gold_badges = Column(Integer, default=0)
    silver_badges = Column(Integer, default=0)
    bronze_badges = Column(Integer, default=0)

    # Activity
    question_count = Column(Integer, default=0)
    answer_count = Column(Integer, default=0)

    # Profile Data
    about_me = Column(Text)
    location = Column(String(255))
    website_url = Column(String(500))
    profile_image_url = Column(String(500))

    # Top Tags
    top_tags = Column(JSONB)  # Array of {tag, score}

    # Raw Data
    raw_data = Column(JSONB)

    # Sync Info
    last_synced_at = Column(DateTime(timezone=True))
    sync_status = Column(String(50), default="pending")
    sync_error = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class MediumProfile(Base):
    __tablename__ = "medium_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Medium Info
    username = Column(String(200), unique=True)
    profile_url = Column(String(500), nullable=False)

    # Profile Data
    name = Column(String(200))
    bio = Column(Text)
    avatar_url = Column(String(500))

    # Stats
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)

    # Raw Data
    raw_data = Column(JSONB)

    # Sync Info
    last_synced_at = Column(DateTime(timezone=True))
    sync_status = Column(String(50), default="pending")
    sync_error = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    articles = relationship("ArticleBlog", back_populates="medium_profile", cascade="all, delete-orphan")


class ArticleBlog(Base):
    __tablename__ = "articles_blogs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    medium_profile_id = Column(UUID(as_uuid=True), ForeignKey("medium_profiles.id", ondelete="SET NULL"))

    # Article Info
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    content = Column(Text)
    excerpt = Column(Text)

    # Metadata
    platform = Column(String(100))  # medium, dev.to, personal blog, etc.
    tags = Column(JSONB)  # Array of tags

    # Stats
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)

    # Dates
    published_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    medium_profile = relationship("MediumProfile", back_populates="articles")


class YouTubeProfile(Base):
    __tablename__ = "youtube_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # YouTube Info
    channel_id = Column(String(200), unique=True)
    channel_url = Column(String(500), nullable=False)
    channel_name = Column(String(200))

    # Profile Data
    description = Column(Text)
    thumbnail_url = Column(String(500))

    # Stats
    subscriber_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)

    # Raw Data
    raw_data = Column(JSONB)

    # OAuth
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime(timezone=True))

    # Sync Info
    last_synced_at = Column(DateTime(timezone=True))
    sync_status = Column(String(50), default="pending")
    sync_error = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    videos = relationship("YouTubeVideo", back_populates="profile", cascade="all, delete-orphan")


class YouTubeVideo(Base):
    __tablename__ = "youtube_videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    youtube_profile_id = Column(UUID(as_uuid=True), ForeignKey("youtube_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Video Info
    video_id = Column(String(200), unique=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    url = Column(String(500))
    thumbnail_url = Column(String(500))

    # Stats
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)

    # Metadata
    duration = Column(String(50))
    tags = Column(JSONB)
    category = Column(String(100))

    # Dates
    published_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    profile = relationship("YouTubeProfile", back_populates="videos")


class IntegrationSyncLog(Base):
    __tablename__ = "integration_sync_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)

    # Sync Info
    platform = Column(String(100), nullable=False, index=True)  # linkedin, github, stackoverflow, etc.
    sync_type = Column(String(50))  # manual, automatic, scheduled
    status = Column(String(50), nullable=False)  # pending, in_progress, completed, failed

    # Details
    items_synced = Column(Integer, default=0)
    error_message = Column(Text)

    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)

    __table_args__ = (
        Index('idx_sync_log_platform', 'candidate_id', 'platform', 'status'),
    )
