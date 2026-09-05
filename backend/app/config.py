import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "PULSE AI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "pulse_ai_super_secret_jwt_key_change_in_production_32bytes")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite+aiosqlite:///./pulse.db"  # Defaults to async sqlite for easy zero-setup local dev/tests, supports PostgreSQL in prod
    )
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://pulse-ai.vercel.app",
    ]

    @property
    def cors_origins(self) -> List[str]:
        origins = list(self.BACKEND_CORS_ORIGINS)
        frontend_url = os.getenv("FRONTEND_URL")
        if frontend_url and frontend_url not in origins:
            origins.append(frontend_url)
        allowed = os.getenv("ALLOWED_ORIGINS")
        if allowed:
            origins.extend([o.strip() for o in allowed.split(",") if o.strip()])
        return origins
    
    # Google OAuth & APIs
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/api/auth/callback/google")
    
    # AI Provider Settings
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")  # openai, gemini, anthropic, mock
    AI_API_KEY: Optional[str] = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4o-mini")
    
    # News API / RSS Settings
    NEWS_API_KEY: Optional[str] = os.getenv("NEWS_API_KEY", "")
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
