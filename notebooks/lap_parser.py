# notebooks/lap_parser.py

import re
from typing import List, Dict, Optional


def extract_lap_info(ocr_results: List) -> Optional[Dict]:
    """
    Extrait les informations de tour depuis les résultats OCR
    Exemple : "LAP 23 /58" → {current_lap: 23, total_laps: 58, progress: 39.7}
    """
    for (bbox, text, prob) in ocr_results:
        text = text.strip()
        match = re.match(r'LAP\s+(\d+)\s*/\s*(\d+)', text, re.IGNORECASE)
        if match:
            current = int(match.group(1))
            total = int(match.group(2))
            return {
                "current_lap": current,
                "total_laps": total,
                "progress_percentage": round((current / total) * 100, 1)
            }
    return None