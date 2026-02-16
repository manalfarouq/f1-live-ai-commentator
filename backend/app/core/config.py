from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    
    # Model Configuration
    MODEL_PATH: str 
    
    # Database Configuration
    DATABASE_URL: str 
    POSTGRES_USER: str 
    POSTGRES_PASSWORD: str 
    POSTGRES_DB: str 
    
    # Security
    SECRET_KEY: str 
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()