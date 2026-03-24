# backend/app/schemas/prediction_schema.py

from pydantic import BaseModel, Field
from typing import Optional


class PredictRequest(BaseModel):
    """Requête de prédiction F1"""

    # Champs obligatoires
    Grid: int = Field(..., ge=1, le=24, description="Position de départ (1-24)")
    Rain: int = Field(..., ge=0, le=1, description="Pluie (0=sec, 1=pluie)")
    Round: int = Field(..., ge=1, le=24, description="Numéro de la course dans la saison")
    Season: int = Field(..., ge=2000, le=2030, description="Année de la course")
    DriverID: str = Field(..., description="ID du pilote (ex: 'max', 'leclerc')")
    ConstructorName: str = Field(..., description="Nom de l'écurie (ex: 'Red Bull', 'Ferrari')")
    CircuitID: str = Field(..., description="ID du circuit (ex: 'monaco', 'spa')")

    # Champs optionnels du modèle v5
    lap: Optional[int] = Field(1, ge=1, description="Tour actuel")
    total_laps: Optional[int] = Field(58, ge=1, description="Nombre total de tours")
    current_position: Optional[int] = Field(None, ge=1, le=24, description="Position actuelle en course")
    lap_time_ms: Optional[float] = Field(90000, description="Dernier temps au tour (ms)")
    avg_lap_time_ms: Optional[float] = Field(90000, description="Temps moyen au tour (ms)")
    best_lap_time_ms: Optional[float] = Field(89000, description="Meilleur temps au tour (ms)")
    nb_pit_stops: Optional[int] = Field(0, ge=0, description="Nombre d'arrêts aux stands")
    gap_to_leader_ms: Optional[float] = Field(0, description="Écart au leader (ms)")
    quali_position: Optional[int] = Field(None, ge=1, le=24, description="Position en qualifications")
    driver_season_points: Optional[float] = Field(0, description="Points au championnat")
    constructor_points: Optional[float] = Field(0, description="Points constructeur")

    model_config = {
        "json_schema_extra": {
            "example": {
                "Grid": 1, "Rain": 0, "Round": 5, "Season": 2026,
                "DriverID": "max", "ConstructorName": "Red Bull", "CircuitID": "monaco",
                "lap": 23, "total_laps": 78, "current_position": 1
            }
        }
    }


class PredictResponse(BaseModel):
    """Réponse de prédiction"""

    winner: bool = Field(..., description="Va gagner la course?")
    probability: float = Field(..., description="Probabilité de victoire (0-100%)")
    prediction: str = Field(..., description="Texte de la prédiction")
    driver: str = Field(..., description="Pilote concerné")
    circuit: str = Field(..., description="Circuit de la course")
    position_predite: Optional[int] = Field(None, description="Position finale prédite (1-20)")
    position_exacte: Optional[float] = Field(None, description="Position exacte avant arrondi")

    model_config = {
        "json_schema_extra": {
            "example": {
                "winner": True, "probability": 87.5,
                "prediction": "max a de fortes chances de gagner à monaco",
                "driver": "max", "circuit": "monaco",
                "position_predite": 1, "position_exacte": 1.23
            }
        }
    }