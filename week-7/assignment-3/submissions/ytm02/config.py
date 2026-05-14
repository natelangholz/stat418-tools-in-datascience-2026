"""Application configuration loaded from environment variables."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central settings object populated from environment / .env file."""

    api_key: str = os.getenv("API_KEY", "")
    model_path: str = os.getenv("MODEL_PATH", "model.pkl")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    max_batch_size: int = int(os.getenv("MAX_BATCH_SIZE", "100"))
    port: int = int(os.getenv("PORT", "8080"))

    model_config = {"env_file": ".env"}


settings = Settings()
