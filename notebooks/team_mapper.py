# notebooks/team_mapper.py
# Données 2026 — générées depuis f1_drivers_2026.xlsx

import os

DRIVER_TEAMS = {
    "VER": "Red Bull Racing",
    "HAD": "Red Bull Racing",
    "NOR": "McLaren",
    "PIA": "McLaren",
    "RUS": "Mercedes",
    "ANT": "Mercedes",
    "HAM": "Ferrari",
    "LEC": "Ferrari",
    "HUL": "Audi",
    "BOR": "Audi",
    "GAS": "Alpine",
    "COL": "Alpine",
    "BOT": "Cadillac",
    "PER": "Cadillac",
    "OCO": "Haas",
    "BEA": "Haas",
    "ALO": "Aston Martin",
    "STR": "Aston Martin",
    "LAW": "Racing Bulls",
    "LIN": "Racing Bulls",
    "TSU": "Racing Bulls",
    "ALB": "Williams",
    "SAI": "Williams",
    # Anciens pilotes (compatibilité)
    "ZHO": "Kick Sauber",
    "MAG": "Haas",
}

DRIVER_NAMES = {
    "VER": "Verstappen",  "HAD": "Hadjar",
    "NOR": "Norris",      "PIA": "Piastri",
    "RUS": "Russell",     "ANT": "Antonelli",
    "HAM": "Hamilton",    "LEC": "Leclerc",
    "HUL": "Hulkenberg",  "BOR": "Bortoleto",
    "GAS": "Gasly",       "COL": "Colapinto",
    "BOT": "Bottas",      "PER": "Perez",
    "OCO": "Ocon",        "BEA": "Bearman",
    "ALO": "Alonso",      "STR": "Stroll",
    "LAW": "Lawson",      "LIN": "Lindblad",
    "TSU": "Tsunoda",     "ALB": "Albon",
    "SAI": "Sainz",
}

# Mots-clés OCR → équipe (pour get_team_from_ocr_text)
OCR_TEAM_KEYWORDS = {
    "Red Bull"   : "Red Bull Racing",
    "McLaren"    : "McLaren",
    "Mercedes"   : "Mercedes",
    "Ferrari"    : "Ferrari",
    "Audi"       : "Audi",
    "Alpine"     : "Alpine",
    "Cadillac"   : "Cadillac",
    "Haas"       : "Haas",
    "Aston"      : "Aston Martin",
    "Williams"   : "Williams",
    "Racing Bulls": "Racing Bulls",
    "RB"         : "Racing Bulls",
}


def load_team_mapping_from_env() -> dict:
    """
    Retourne le mapping pilote → équipe.
    Conservée pour compatibilité avec driver_parser.py et analyse_frame.py.
    """
    return DRIVER_TEAMS.copy()


def get_team_from_ocr_text(text: str) -> str:
    """
    Tente de détecter une équipe dans un texte OCR brut.
    Retourne None si aucune équipe trouvée.
    """
    for keyword, team in OCR_TEAM_KEYWORDS.items():
        if keyword.lower() in text.lower():
            return team
    return None


def get_team(driver_code: str) -> str:
    """Retourne le nom de l'équipe pour un code pilote"""
    return DRIVER_TEAMS.get(driver_code.upper(), "Unknown")


def get_full_name(driver_code: str) -> str:
    """Retourne le nom complet pour un code pilote"""
    return DRIVER_NAMES.get(driver_code.upper(), driver_code)


def get_driver_info(driver_code: str) -> dict:
    """Retourne toutes les infos d'un pilote"""
    code = driver_code.upper()
    return {
        "code": code,
        "name": DRIVER_NAMES.get(code, code),
        "team": DRIVER_TEAMS.get(code, "Unknown"),
    }