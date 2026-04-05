import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://security_user:password@localhost/security_incidents"

    # Encryption
    vault_master_key: str = "0000000000000000000000000000000000000000000000000000000000000000"
    audit_log_signing_key: str = "0000000000000000000000000000000000000000000000000000000000000000"

    # JWT
    jwt_secret_key: str = "change_this_to_a_random_string_in_production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_queue_name: str = "anonymization_queue"

    # Security
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    rate_limit_per_minute: int = 60
    max_upload_size_mb: int = 50

    # OpenAI
    openai_api_key: str = ""

    # Model
    default_model_version: str = "v1.0.0"
    min_classification_confidence: float = 0.80

    # Retention
    vault_retention_days: int = 2555

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Constants
DATABASE_URL = settings.database_url
VAULT_MASTER_KEY = settings.vault_master_key
AUDIT_LOG_SIGNING_KEY = settings.audit_log_signing_key
JWT_SECRET_KEY = settings.jwt_secret_key
JWT_ALGORITHM = settings.jwt_algorithm
REDIS_URL = settings.redis_url
OPENAI_API_KEY = settings.openai_api_key
