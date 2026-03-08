# notebooks/lap_parser.py

import re
from typing import List, Dict, Optional


def extract_lap_info(ocr_results: List) -> Optional[Dict]:
    """
    Extrait les informations de tour depuis les résultats OCR.

    Gère les formats OCR bruités :
    - "LAP 23 / 58"  → slash lisible
    - "LAP 2158"     → slash lu comme "1" par l'OCR
    - "LAP 2 /58"    → slash séparé
    - "LAP" + "2/58" → tokens séparés
    """
    texts = [text.strip() for (_, text, _) in ocr_results]

    # ── Tentative 1 : slash normal dans un seul token ─────────────────────
    for text in texts:
        match = re.search(r'LAP\s+(\d+)\s*/\s*(\d+)', text, re.IGNORECASE)
        if match:
            return _build(int(match.group(1)), int(match.group(2)))

    # ── Tentative 2 : slash lu comme "1" → "LAP 2158" = LAP 2/58 ─────────
    # Pattern : LAP + nombre collé où le "/" manque → on cherche LAPXYYY
    # où X est le tour (1-2 chiffres) et YYY est le total (2-3 chiffres)
    for text in texts:
        match = re.search(r'LAP\s+(\d{1,2})1(\d{2,3})\b', text, re.IGNORECASE)
        if match:
            current = int(match.group(1))
            total   = int(match.group(2))
            if 1 <= current < total <= 200:
                return _build(current, total)

    # ── Tentative 3 : "LAP X" suivi de "/ Y" dans les tokens voisins ──────
    for i, text in enumerate(texts):
        lap_match = re.match(r'^LAP\s+(\d+)$', text, re.IGNORECASE)
        if lap_match:
            current = int(lap_match.group(1))
            for j in range(i + 1, min(i + 4, len(texts))):
                total_match = re.search(r'1?(\d{2,3})', texts[j])
                if total_match:
                    total = int(total_match.group(1))
                    if total > current:
                        return _build(current, total)
            break

    # ── Tentative 4 : cherche "X / Y" ou "X1Y" n'importe où ──────────────
    full_text = ' '.join(texts)
    match = re.search(r'\b(\d{1,2})\s*/\s*(\d{2,3})\b', full_text)
    if match:
        c, t = int(match.group(1)), int(match.group(2))
        if 1 <= c < t <= 200:
            return _build(c, t)

    return None


def _build(current: int, total: int) -> Dict:
    return {
        "current_lap"        : current,
        "total_laps"         : total,
        "progress_percentage": round((current / total) * 100, 1),
    }