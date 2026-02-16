from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    APP_NAME: str = "F1 Live AI Commentator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Model Settings
    MODEL_PATH: str = "app/models/f1_winner_model.joblib"
    
    # Optional: Auth settings (pour plus tard)
    SK: str = "your-secret-key-change-this"
    ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 heures
    
    class Config:
        env_file = ".env"

settings = Settings()
