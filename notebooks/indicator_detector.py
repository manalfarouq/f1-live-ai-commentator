# notebooks/indicator_detector.py

import cv2
import numpy as np
from typing import Dict, Optional

# Couleurs des indicateurs F1 en BGR
# Violet = fastest lap (chrono), Jaune = warning, Rouge = danger
INDICATOR_COLORS = {
    "fastest_lap": {"b": (130, 255), "g": (0, 80),   "r": (130, 255)},  # Violet 🟣
    "warning":     {"b": (0, 80),   "g": (180, 255), "r": (180, 255)},  # Jaune 🟡
    "danger":      {"b": (0, 80),   "g": (0, 80),    "r": (180, 255)},  # Rouge 🔴 
}


def is_color_match(b: float, g: float, r: float, color_range: Dict) -> bool:
    """
    Vérifie si une couleur BGR correspond à un indicateur connu
    """
    return (
        color_range["b"][0] <= b <= color_range["b"][1] and
        color_range["g"][0] <= g <= color_range["g"][1] and
        color_range["r"][0] <= r <= color_range["r"][1]
    )


def detect_indicator_in_region(region) -> Optional[str]:
    """
    Détecte le type d'indicateur dans une région de l'image
    Retourne le nom de l'indicateur ou None
    """
    if region is None or region.size == 0:
        return None

    mean_color = np.mean(region.reshape(-1, 3), axis=0)
    b, g, r = mean_color

    for name, color_range in INDICATOR_COLORS.items():
        if is_color_match(b, g, r, color_range):
            return name

    return None


def detect_row_indicators(image_path: str, num_drivers: int = 20) -> Dict[int, str]:
    """
    Détecte les indicateurs visuels (chrono, warning, danger) pour chaque pilote
    Retourne : {position: indicator_type}
    Exemple  : {10: "fastest_lap", 3: "warning"}

    Calibration basée sur l'image F1 :
    - y_start  : position Y du premier pilote (~80px)
    - row_height: hauteur de chaque ligne (~32px)
    - x_start  : zone droite de la barre (derniers 40px)
    """
    image = cv2.imread(image_path)
    if image is None:
        return {}

    height, width = image.shape[:2]

    x_start = width - 40
    x_end = width
    y_start = 80
    row_height = 32

    indicators = {}

    for pos in range(1, num_drivers + 1):
        y_center = y_start + (pos - 1) * row_height
        y_top = max(0, y_center - 10)
        y_bottom = min(height, y_center + 10)

        region = image[y_top:y_bottom, x_start:x_end]
        indicator = detect_indicator_in_region(region)

        if indicator:
            indicators[pos] = indicator

    return indicators