"""Application configuration loaded from environment variables or a .env file."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the API."""

    api_key: str = "changeme"
    model_path: str = "model.pkl"
    log_level: str = "INFO"
    max_batch_size: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        protected_namespaces=(),
    )


settings = Settings()
