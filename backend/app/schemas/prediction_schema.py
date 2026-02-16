from pydantic import BaseModel, Field
from typing import Optional

class PredictRequest(BaseModel):
    """Requête de prédiction F1"""
    Grid: int = Field(..., ge=1, le=24, description="Position de départ (1-24)")
    Rain: int = Field(..., ge=0, le=1, description="Pluie (0=sec, 1=pluie)")
    Round: int = Field(..., ge=1, le=24, description="Numéro de la course dans la saison")
    Season: int = Field(..., ge=2000, le=2030, description="Année de la course")
    DriverID: str = Field(..., description="ID du pilote (ex: 'max', 'lewis')")
    ConstructorName: str = Field(..., description="Nom de l'écurie (ex: 'Red Bull', 'Mercedes')")
    CircuitID: str = Field(..., description="ID du circuit (ex: 'monaco', 'spa')")
    
    class Config:
        json_schema_extra = {
            "example": {
                "Grid": 1,
                "Rain": 0,
                "Round": 5,
                "Season": 2026,
                "DriverID": "max",
                "ConstructorName": "Red Bull",
                "CircuitID": "monaco"
            }
        }

class PredictResponse(BaseModel):
    """Réponse de prédiction"""
    winner: bool = Field(..., description="Va gagner la course?")
    probability: float = Field(..., description="Probabilité de victoire (0-100%)")
    prediction: str = Field(..., description="Texte de la prédiction")
    driver: str = Field(..., description="Pilote concerné")
    circuit: str = Field(..., description="Circuit de la course")
    
    class Config:
        json_schema_extra = {
            "example": {
                "winner": True,
                "probability": 87.5,
                "prediction": "Max Verstappen a de fortes chances de gagner à Monaco",
                "driver": "max",
                "circuit": "monaco"
            }
        }
