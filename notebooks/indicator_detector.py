# notebooks/indicator_detector.py

import cv2
from ultralytics import YOLO
from typing import Dict, Optional


# Paramètres
MODEL_PATH = "models/yolo_f1_indicators.pt"

# Correspondance classes YOLO → noms métier
# On garde les mêmes noms qu'avant pour ne pas casser le reste du pipeline
YOLO_TO_INDICATOR = {
    "purple stopwatch icon":  "fastest_lap",
    "Yellow exclamation mark": "warning",
    "Red exclamation mark":    "danger",
    "Yellow flag":             "yellow_flag",
    "Red flag":                "red_flag",
    "Green flag":              "green_flag",
    "Safety Car":              "safety_car",
    "Virtual Safety Car":      "vsc",
    "in pit":                  "in_pit",
    "out":                     "out",
    "Checkered":               "checkered",
    "VSC ending":              "vsc_ending",
}

# Calibration des lignes (même que l'ancienne version)
Y_START    = 80   # position Y du premier pilote
ROW_HEIGHT = 32   # hauteur de chaque ligne



# Chargement du modèle
"""
On charge le modèle une seule fois au démarrage du module.
Comme ça, on ne recharge pas le .pt à chaque appel de fonction.
"""
_model: Optional[YOLO] = None

def get_model() -> YOLO:
    global _model
    if _model is None:
        _model = YOLO(MODEL_PATH)
    return _model



# Conversion bbox → position pilote
def bbox_to_position(y_center: float) -> int:
    """
    Convertit la coordonnée Y du centre d'une bbox
    en numéro de position du pilote (1 à 20)
    """
    pos = round((y_center - Y_START) / ROW_HEIGHT) + 1
    return max(1, min(20, pos))



# Détection principale
def detect_row_indicators(image_path: str, num_drivers: int = 20) -> Dict[int, str]:
    """
    Détecte les indicateurs visuels F1 avec YOLOv8
    Retourne : {position: indicator_type}
    Exemple  : {2: "fastest_lap", 19: "warning"}

    Remplace l'ancienne détection par couleur BGR —
    YOLO est plus robuste aux variations de luminosité et de résolution.
    """
    model   = get_model()
    results = model(image_path, verbose=False)

    indicators = {}

    for result in results:
        for box in result.boxes:

            # Nom de la classe détectée
            class_name = result.names[int(box.cls)]

            # Ignorer les classes qui n'ont pas de correspondance métier
            if class_name not in YOLO_TO_INDICATOR:
                continue

            # Position Y du centre de la bbox → numéro de pilote
            y_center = float(box.xyxy[0][1] + box.xyxy[0][3]) / 2
            position = bbox_to_position(y_center)

            indicators[position] = YOLO_TO_INDICATOR[class_name]

    return indicators