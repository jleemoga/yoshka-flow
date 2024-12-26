from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    # API settings
    APP_NAME: str = "YoshkaFlow API"
    DEBUG: bool = False  # Default to False for security
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    
    # Redis settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USERNAME: str = "default"
    REDIS_PASSWORD: str
    
    # Database settings
    POSTGRES_URL: str = "postgresql://yoshka-dev_owner:78BiuHLyjAnw@ep-round-resonance-a5gemu9b.us-east-2.aws.neon.tech/yoshka-dev?sslmode=require"
    
    @property
    def REDIS_URL(self) -> str:
        """Constructs Redis URL with authentication"""
        return f"redis://{self.REDIS_USERNAME}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()
