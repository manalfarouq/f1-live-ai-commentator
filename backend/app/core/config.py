# backend/app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# En local  : backend/app/core/config.py → parents[2] = backend/ → pas bon non plus
# En Docker : /app/app/core/config.py    → parents[2] = /app/
# La solution : utiliser une variable d'env, avec fallback intelligent

_THIS_FILE = Path(__file__).resolve()

# parents[2] = le dossier qui contient "app/" (backend/ en local, /app/ en Docker)
ROOT_DIR = _THIS_FILE.parents[2]

class Settings(BaseSettings):
    MODEL_PATH: str
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    GEMINI_API_KEY: str
    HF_TOKEN: str = ""

    F1_PDF_PATH: str = str(ROOT_DIR / "data/rag/f1_regles.pdf")
    CHROMA_DIR: str  = str(ROOT_DIR / "data/rag/chroma_db")
    COLLECTION_NAME: str = "f1_knowledge"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 80
    EMBED_MODEL: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = str(ROOT_DIR / ".env")
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()