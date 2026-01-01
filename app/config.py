from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    
    # Database - PostgreSQL for production, SQLite for development
    database_url: str = "sqlite:///./mnam.db"
    
    # Security
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # AI
    gemini_api_key: str = ""
    
    # CORS - Frontend URL
    frontend_url: str = "http://localhost:5173"
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def cors_origins(self) -> list:
        """Get allowed CORS origins based on environment"""
        if self.is_production:
            return [
                self.frontend_url,
                # Add any additional production domains here
            ]
        else:
            return [
                self.frontend_url,
                "http://localhost:5173",
                "http://localhost:3000",
                "http://localhost:3001",
                "http://localhost:3002",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
                "http://127.0.0.1:3002",
            ]
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
