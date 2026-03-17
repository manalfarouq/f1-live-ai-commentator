# backend/app/models/f1_models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Race(Base):
    """Modèle pour une course F1"""
    __tablename__ = "races"
    
    id = Column(Integer, primary_key=True, index=True)
    race_name = Column(String, nullable=True)
    circuit = Column(String, nullable=True)
    current_lap = Column(Integer, nullable=False)
    total_laps = Column(Integer, nullable=False)
    progress_percentage = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relation avec les positions
    positions = relationship("RacePosition", back_populates="race", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Race {self.race_name or 'Unknown'} - Lap {self.current_lap}/{self.total_laps}>"


class RacePosition(Base):
    """Modèle pour la position d'un pilote à un moment donné"""
    __tablename__ = "race_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.id"), nullable=False)
    
    position = Column(Integer, nullable=False)
    driver = Column(String(3), nullable=False)
    team = Column(String, nullable=False)
    interval = Column(String, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relation avec la course
    race = relationship("Race", back_populates="positions")
    
    def __repr__(self):
        return f"<Position P{self.position} - {self.driver} ({self.team})>"