# notebooks/reconnaissance_dobjets.py

from ocr_extractor import extract_text_from_image
from lap_parser import extract_lap_info
from driver_parser import parse_driver_data
from indicator_detector import detect_row_indicators
from typing import Dict


def get_f1_data(image_path: str) -> Dict:
    """
    Fonction principale - Orchestre toutes les extractions F1
    """
    ocr_results = extract_text_from_image(image_path)

    return {
        "drivers":    parse_driver_data(ocr_results),
        "lap_info":   extract_lap_info(ocr_results),
        "indicators": detect_row_indicators(image_path)
    }


def save_data_to_dict(f1_data: Dict) -> Dict:
    """
    Transforme en dictionnaire structuré pour l'API
    Injecte les indicateurs dans les données de chaque pilote
    """
    drivers    = f1_data.get("drivers", [])
    lap_info   = f1_data.get("lap_info")
    indicators = f1_data.get("indicators", {})

    # Injecter l'indicateur dans les données du pilote concerné
    for driver in drivers:
        pos = driver.get("position")
        if pos in indicators:
            driver["indicator"] = indicators[pos]

    result = {
        "total_drivers": len(drivers),
        "drivers":       drivers,
        "leader":        drivers[0] if drivers else None
    }

    if lap_info:
        result["lap_info"] = lap_info

    return result