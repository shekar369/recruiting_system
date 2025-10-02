from pydantic_settings import BaseSettings
from typing import List
import os


def parse_cors_origins(v: str) -> List[str]:
    if isinstance(v, str):
        return [i.strip() for i in v.split(',')]
    return v


class Settings(BaseSettings):
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "RAG Recruiting System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/recruiting_db"
    ASYNC_DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/recruiting_db"

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return parse_cors_origins(self.CORS_ORIGINS)

    # Storage
    UPLOAD_DIR: str = "./uploads"
    FAISS_INDEX_PATH: str = "./data/faiss_index"
    MODEL_CACHE_PATH: str = "./data/models"

    # Embedding Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # LLM Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"

    LLM_PROVIDER: str = "ollama"

    # OAuth - LinkedIn
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    LINKEDIN_REDIRECT_URI: str = "http://localhost:8000/api/v1/integrations/linkedin/callback"

    # OAuth - GitHub
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/v1/integrations/github/callback"

    # Search Configuration
    SEARCH_TOP_K: int = 100
    RERANK_TOP_K: int = 20

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "resumes"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "documents"), exist_ok=True)
os.makedirs(settings.FAISS_INDEX_PATH, exist_ok=True)
os.makedirs(settings.MODEL_CACHE_PATH, exist_ok=True)
