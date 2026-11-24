from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    PROJECT_NAME: str = "AI-Powered Pharma RCA Module"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # PostgreSQL Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "pharma_rca_db"

    # Async & Sync Database URLs
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/pharma_rca_db"
    DATABASE_SYNC_URL: str = "postgresql://postgres:postgres@127.0.0.1:5432/pharma_rca_db"

    # Groq AI Settings
    GROQ_API_KEY: str = "gsk_placeholder_for_local_dev"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
