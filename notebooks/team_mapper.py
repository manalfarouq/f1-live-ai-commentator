# notebooks/team_mapper.py

import os
from typing import Dict, Optional

# Codes d'équipe détectables dans le texte OCR brut
# Exemple : "13 W ALB" → W = Williams
TEAM_CODE_MAPPING = {
    'W': 'Williams',
    'P8': 'Haas',
    '44': 'Mercedes'
}

# Mapping par défaut (fallback si .env absent)
DEFAULT_FALLBACK = {
    'VER': 'Red Bull Racing', 'PER': 'Red Bull Racing',
    'HAM': 'Ferrari',         'RUS': 'Mercedes',
    'LEC': 'Ferrari',         'SAI': 'Williams',
    'NOR': 'McLaren',         'PIA': 'McLaren',
    'ALO': 'Aston Martin',    'STR': 'Aston Martin',
    'OCO': 'Alpine',          'GAS': 'Alpine',
    'TSU': 'RB',              'LAW': 'RB',
    'ALB': 'Williams',        'COL': 'Williams',
    'HUL': 'Haas',            'MAG': 'Haas',
    'BOT': 'Kick Sauber',     'ZHO': 'Kick Sauber',
    'BOR': 'Williams',        'BEA': 'Haas',
    'HAD': 'Haas',            'ANT': 'Mercedes'
}

def load_team_mapping_from_env() -> Dict[str, str]:
    """
    Charge le mapping des équipes depuis les variables d'environnement .env
    Exemple : F1_TEAM_HAM=Ferrari → {'HAM': 'Ferrari'}
    Fallback sur DEFAULT_FALLBACK si aucune variable trouvée
    """
    drivers = list(DEFAULT_FALLBACK.keys())
    
    team_mapping = {}
    for driver in drivers:
        team = os.getenv(f'F1_TEAM_{driver}')
        if team:
            team_mapping[driver] = team
    
    # Si aucune variable d'env trouvée → fallback
    if not team_mapping:
        return DEFAULT_FALLBACK.copy()
    
    return team_mapping


def get_team_from_ocr_text(text: str) -> Optional[str]:
    """
    Extrait le nom d'équipe depuis un texte OCR brut
    Exemple : "13 W ALB" → "Williams"
    """
    for code, team in TEAM_CODE_MAPPING.items():
        if code in text:
            return team
    return None