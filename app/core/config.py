from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "LMS FastAPI"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database settings
    DATABASE_URL: str = "mssql+pyodbc://DESKTOP-OU0VU87\\SQLEXPRESS/FastApiDb?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()