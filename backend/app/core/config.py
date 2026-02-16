from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Model Settings
    MODEL_PATH: str 
    
    # Optional: Auth settings 
    SK: str 
    ALG: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 heures
    
    class Config:
        env_file = ".env"

settings = Settings()
