# backend/app/services/f1_db_service.py

from sqlalchemy.orm import Session
from app.models.f1_models import Race, RacePosition
from typing import Dict, List
from datetime import datetime


def save_race_data(db: Session, f1_data: Dict, race_name: str = None, circuit: str = None) -> Race:
    """
    Sauvegarde les données d'une course dans la base de données
    """
    lap_info = f1_data.get("lap_info", {})
    drivers = f1_data.get("drivers", [])
    
    # Créer la course
    race = Race(
        race_name=race_name,
        circuit=circuit,
        current_lap=lap_info.get("current_lap", 0),
        total_laps=lap_info.get("total_laps", 0),
        progress_percentage=lap_info.get("progress_percentage", 0.0),
        timestamp=datetime.utcnow()
    )
    
    db.add(race)
    db.flush()  # Pour obtenir l'ID de la course
    
    # Créer les positions
    for driver_data in drivers:
        position = RacePosition(
            race_id=race.id,
            position=driver_data.get("position"),
            driver=driver_data.get("driver"),
            team=driver_data.get("team"),
            interval=driver_data.get("interval")
        )
        db.add(position)
    
    db.commit()
    db.refresh(race)
    
    return race


def get_race_by_id(db: Session, race_id: int) -> Race:
    """
    Récupère une course par son ID
    """
    return db.query(Race).filter(Race.id == race_id).first()


def get_all_races(db: Session, limit: int = 50) -> List[Race]:
    """
    Récupère toutes les courses (limité à 50 par défaut)
    """
    return db.query(Race).order_by(Race.timestamp.desc()).limit(limit).all()


def get_driver_history(db: Session, driver_code: str, limit: int = 20) -> List[RacePosition]:
    """
    Récupère l'historique des positions d'un pilote
    """
    return db.query(RacePosition).filter(
        RacePosition.driver == driver_code
    ).order_by(RacePosition.timestamp.desc()).limit(limit).all()


def get_race_positions(db: Session, race_id: int) -> List[RacePosition]:
    """
    Récupère toutes les positions pour une course donnée
    """
    return db.query(RacePosition).filter(
        RacePosition.race_id == race_id
    ).order_by(RacePosition.position).all()