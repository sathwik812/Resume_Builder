import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings - ignores extra fields in .env"""
    GOOGLE_API_KEY: str = ""  
    EMBEDDING_MODEL_NAME: str = "models/embedding-001"  
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SENDER_EMAIL: str = ""
    SENDER_PASSWORD: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields that aren't defined here
        case_sensitive=False
    )

settings = Settings()
if settings.GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY