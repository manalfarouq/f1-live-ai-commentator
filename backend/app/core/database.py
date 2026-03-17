from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://f1user:f1password@localhost:5432/f1_predictions")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class EncodingMapping(Base):
    __tablename__ = "encoding_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)  # 'driver', 'constructor', 'circuit'
    name = Column(String, index=True)
    code = Column(Integer)


def init_db():
    """Initialiser la base de données"""
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()