from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "mysql+aiomysql://ai_interview_user:AiInterview2024@localhost:3306/ai_interview"

    
    # JWT Configuration
    secret_key: str = "ACfanZbPbcTBHzojsevt7FZ2Q_W1tLKLK7Z9uc4mWFQ"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60  # Extended to 1 hour for development
    refresh_token_expire_days: int = 7
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS Configuration
    allowed_origins: str = "http://localhost:3000"
    
    # File Upload Configuration
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "uploads"
    allowed_extensions: str = "pdf,doc,docx,txt,mp3,mp4,wav,avi"
    
    # AI Services Configuration
    transcription_provider: str = "whisper"  # whisper, openai, huggingface
    openai_api_key: Optional[str] = ""
    huggingface_api_key: str = "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"
    tts_provider: str = "coqui"  # coqui, huggingface

    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    openai_model_name: str = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
    google_model_name: str = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.0-flash")
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.allowed_extensions.split(",")]

# Create settings instance
settings = Settings()