from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    # --- ce que j'avais déjà ---
    MODEL_PATH: str

    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # --- APIs ---
    GEMINI_API_KEY: str
    HF_TOKEN: str = ""

    # --- RAG : j'ai juste ajouté ces 6 lignes ---
    # où est le PDF qu'on a créé ensemble
    F1_PDF_PATH: str = "data/rag/f1_regles.pdf"

    # où ChromaDB va stocker la base vectorielle
    CHROMA_DIR: str = "data/rag/chroma_db"

    # nom de la collection dans ChromaDB
    COLLECTION_NAME: str = "f1_knowledge"

    # taille d'un morceau de texte (~3 phrases)
    CHUNK_SIZE: int = 500

    # chevauchement entre deux morceaux (évite de couper une règle en 2)
    CHUNK_OVERLAP: int = 80

    # modèle qui transforme le texte en vecteurs
    EMBED_MODEL: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore" 


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()