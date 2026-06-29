import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Kairos Assistant API"
    debug: bool = False

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://kairos:kairos2026@localhost:5432/kairos_assistant",
    )

    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "openrouter/auto")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    jwt_secret: str = os.getenv("JWT_SECRET", "kairos-dev-secret-change-in-prod")
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    cors_origins: list[str] = ["*"]

    aion_base_url: str = os.getenv("AION_BASE_URL", "http://localhost:8080")
    aion_api_key: str = os.getenv("AION_API_KEY", "")


settings = Settings()
