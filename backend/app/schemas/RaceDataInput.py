
from pydantic import BaseModel
from typing import Optional
from .DriverInfo import DriverInfo

class RaceDataInput(BaseModel):
    """
    Ce que ton Driver Parser produit après YOLO + OCR.
    Correspond exactement à la sortie de ton pipeline existant.
    """
    event      : str                        # "flag", "pit", "safety_car", etc.
    flag_type  : Optional[str] = None       # "yellow", "red", "blue"...
    tyre_type  : Optional[str] = None       # "soft", "medium", "hard"...
    lap        : Optional[int] = None
    total_laps : Optional[int] = None
    drivers    : Optional[list[DriverInfo]] = []
    predictions: Optional[dict] = {}
    persona    : Optional[str] = "journaliste"  # persona demandé par le front