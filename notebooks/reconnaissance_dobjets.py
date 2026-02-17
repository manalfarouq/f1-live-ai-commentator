# notebooks/reconnaissance_dobjets.py

import cv2
import easyocr
import re
import os
from typing import List, Dict, Optional

reader = None

# Mapping des codes d'équipe détectés dans l'OCR
TEAM_CODE_MAPPING = {
    'W': 'Williams',
    'P8': 'Haas',
    '44': 'Mercedes'
}

def load_team_mapping_from_env() -> Dict[str, str]:
    """
    Charge le mapping des équipes depuis les variables d'environnement
    """
    team_mapping = {}
    
    # Liste des pilotes à chercher
    drivers = [
        'VER', 'PER', 'HAM', 'RUS', 'LEC', 'SAI', 'NOR', 'PIA',
        'ALO', 'STR', 'OCO', 'GAS', 'TSU', 'LAW', 'ALB', 'COL',
        'HUL', 'MAG', 'BOT', 'ZHO', 'BOR', 'BEA', 'HAD', 'ANT'
    ]
    
    for driver in drivers:
        env_key = f'F1_TEAM_{driver}'
        team = os.getenv(env_key)
        if team:
            team_mapping[driver] = team
    
    # Mapping par défaut si pas de .env
    if not team_mapping:
        team_mapping = {
            'VER': 'Red Bull Racing', 'PER': 'Red Bull Racing',
            'HAM': 'Ferrari', 'RUS': 'Mercedes',
            'LEC': 'Ferrari', 'SAI': 'Williams',
            'NOR': 'McLaren', 'PIA': 'McLaren',
            'ALO': 'Aston Martin', 'STR': 'Aston Martin',
            'OCO': 'Alpine', 'GAS': 'Alpine',
            'TSU': 'RB', 'LAW': 'RB',
            'ALB': 'Williams', 'COL': 'Williams',
            'HUL': 'Haas', 'MAG': 'Haas',
            'BOT': 'Kick Sauber', 'ZHO': 'Kick Sauber',
            'BOR': 'Williams', 'BEA': 'Haas', 'HAD': 'Haas', 'ANT': 'Mercedes'
        }
    
    return team_mapping

# Charger le mapping au démarrage
DEFAULT_TEAM_MAPPING = load_team_mapping_from_env()

def init_reader():
    """Initialise le lecteur OCR une seule fois"""
    global reader
    if reader is None:
        reader = easyocr.Reader(['en'], gpu=False)
    return reader

def extract_text_from_image(image_path: str) -> List:
    """
    Extrait tout le texte d'une image F1
    """
    ocr_reader = init_reader()
    image = cv2.imread(image_path)
    results = ocr_reader.readtext(image, detail=1, paragraph=False)
    return results

def extract_lap_info(ocr_results: List) -> Optional[Dict]:
    """
    Extrait les informations de tour (LAP 23 /58)
    """
    for (bbox, text, prob) in ocr_results:
        text = text.strip()
        match = re.match(r'LAP\s+(\d+)\s*/\s*(\d+)', text, re.IGNORECASE)
        if match:
            return {
                "current_lap": int(match.group(1)),
                "total_laps": int(match.group(2)),
                "progress_percentage": round((int(match.group(1)) / int(match.group(2))) * 100, 1)
            }
    return None

def extract_team_from_text(text: str) -> Optional[str]:
    """
    Extrait le code d'équipe depuis le texte OCR
    """
    for code, team in TEAM_CODE_MAPPING.items():
        if code in text:
            return team
    return None

def parse_driver_data(ocr_results: List) -> List[Dict]:
    """
    Parse les résultats OCR avec équipes
    """
    sorted_results = sorted(ocr_results, key=lambda x: x[0][0][1])
    
    valid_drivers = {
        'VER', 'PIA', 'NOR', 'TSU', 'LEC', 'RUS', 'STR', 'ANT', 
        'HAM', 'HUL', 'ALO', 'BOR', 'ALB', 'HAD', 'BEA', 'OCO', 
        'SAI', 'GAS', 'COL', 'LAW', 'PER', 'ZHO', 'MAG', 'BOT'
    }
    
    drivers_dict = {}
    position_counter = 1
    processed_indices = set()
    
    i = 0
    while i < len(sorted_results):
        if i in processed_indices:
            i += 1
            continue
            
        bbox, text, prob = sorted_results[i]
        text = text.strip()
        current_y = bbox[0][1]
        
        # Cas 1 : Position + pilote
        match = re.match(r'^(\d{1,2})\s.*?([A-Z]{3})', text)
        if match:
            pos = int(match.group(1))
            pilot = match.group(2)
            if 1 <= pos <= 20 and pilot in valid_drivers:
                team_from_ocr = extract_team_from_text(text)
                team = team_from_ocr if team_from_ocr else DEFAULT_TEAM_MAPPING.get(pilot, 'Unknown')
                
                drivers_dict[pos] = {
                    'position': pos, 
                    'driver': pilot,
                    'team': team
                }
                processed_indices.add(i)
                
                interval_match = re.search(r'\+[\d.]+\s*H', text)
                if interval_match:
                    drivers_dict[pos]['interval'] = interval_match.group(0)
                else:
                    if i+1 < len(sorted_results):
                        _, next_text, _ = sorted_results[i+1]
                        if '+' in next_text:
                            drivers_dict[pos]['interval'] = next_text
                            processed_indices.add(i+1)
                
                i += 1
                continue
        
        # Cas 2 : Position seule
        if re.match(r'^\d{1,2}$', text):
            pos = int(text)
            if 1 <= pos <= 20 and pos not in drivers_dict:
                drivers_dict[pos] = {'position': pos}
                processed_indices.add(i)
                
                for j in range(i+1, min(i+4, len(sorted_results))):
                    if j in processed_indices:
                        continue
                        
                    next_bbox, next_text, _ = sorted_results[j]
                    next_y = next_bbox[0][1]
                    next_text_clean = next_text.strip()
                    
                    if abs(next_y - current_y) > 20:
                        break
                    
                    if 'driver' not in drivers_dict[pos]:
                        pilot_match = re.search(r'([A-Za-z]{3})', next_text_clean)
                        if pilot_match:
                            pilot_candidate = pilot_match.group(1).upper()
                            if pilot_candidate in valid_drivers:
                                drivers_dict[pos]['driver'] = pilot_candidate
                                drivers_dict[pos]['team'] = DEFAULT_TEAM_MAPPING.get(pilot_candidate, 'Unknown')
                                processed_indices.add(j)
                    
                    if 'interval' not in drivers_dict[pos] and ('+' in next_text_clean or 'Interval' in next_text_clean):
                        drivers_dict[pos]['interval'] = next_text_clean
                        processed_indices.add(j)
                
                i += 1
                continue
        
        # Cas 3 : Pilote + intervalle
        match = re.match(r'^([A-Z]{3})\s(\+[\d.]+\s*H)', text)
        if match:
            pilot = match.group(1)
            interval = match.group(2)
            if pilot in valid_drivers:
                while position_counter in drivers_dict:
                    position_counter += 1
                
                if position_counter <= 20:
                    drivers_dict[position_counter] = {
                        'position': position_counter,
                        'driver': pilot,
                        'team': DEFAULT_TEAM_MAPPING.get(pilot, 'Unknown'),
                        'interval': interval
                    }
                    processed_indices.add(i)
                    position_counter += 1
                i += 1
                continue
        
        # Cas 4 : Pilote seul
        if text in valid_drivers or text.upper() in valid_drivers:
            pilot = text.upper() if text.upper() in valid_drivers else text
            
            while position_counter in drivers_dict:
                position_counter += 1
            
            if position_counter <= 20:
                drivers_dict[position_counter] = {
                    'position': position_counter, 
                    'driver': pilot,
                    'team': DEFAULT_TEAM_MAPPING.get(pilot, 'Unknown')
                }
                processed_indices.add(i)
                
                if i+1 < len(sorted_results) and (i+1) not in processed_indices:
                    _, next_text, _ = sorted_results[i+1]
                    if '+' in next_text or 'Interval' in next_text:
                        drivers_dict[position_counter]['interval'] = next_text
                        processed_indices.add(i+1)
                
                position_counter += 1
        
        i += 1
    
    drivers = sorted(drivers_dict.values(), key=lambda x: x['position'])
    return drivers

def get_f1_data(image_path: str) -> Dict:
    """
    Fonction principale
    """
    ocr_results = extract_text_from_image(image_path)
    drivers_data = parse_driver_data(ocr_results)
    lap_info = extract_lap_info(ocr_results)
    
    return {
        "drivers": drivers_data,
        "lap_info": lap_info
    }

def save_data_to_dict(f1_data: Dict) -> Dict:
    """
    Transforme en dictionnaire structuré
    """
    drivers = f1_data.get("drivers", [])
    lap_info = f1_data.get("lap_info")
    
    result = {
        "total_drivers": len(drivers),
        "drivers": drivers,
        "leader": drivers[0] if drivers else None
    }
    
    if lap_info:
        result["lap_info"] = lap_info
    
    return result