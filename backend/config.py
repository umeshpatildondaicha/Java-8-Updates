from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    DATA_DIR: str = "./data"
    UPLOAD_DIR: str = "./data/uploads"
    OUTPUT_DIR: str = "./data/output"
    MAX_UPLOAD_MB: int = 500

    class Config:
        env_file = ".env"


settings = Settings()

# Ensure dirs exist on import
for d in [settings.DATA_DIR, settings.UPLOAD_DIR, settings.OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)
