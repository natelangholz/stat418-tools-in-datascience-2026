import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_key: str = os.getenv("API_KEY", "test123")
    model_path: str = os.getenv("MODEL_PATH", "model.pkl")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    max_batch_size: int = int(os.getenv("MAX_BATCH_SIZE", "100"))

    class Config:
        env_file = ".env"


settings = Settings()

