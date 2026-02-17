# notebooks/reconnaissance_dobjets.py

import cv2
import easyocr
import re
from typing import List, Dict

reader = None

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

def parse_driver_data(ocr_results: List) -> List[Dict]:
    """
    Parse les résultats OCR - Version finale
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
        
        # Cas 1 : Position + pilote (PRIORITÉ)
        match = re.match(r'^(\d{1,2})\s.*?([A-Z]{3})', text)
        if match:
            pos = int(match.group(1))
            pilot = match.group(2)
            if 1 <= pos <= 20 and pilot in valid_drivers:
                drivers_dict[pos] = {'position': pos, 'driver': pilot}
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
                    
                    # Pilote (même mal écrit comme "44 cOL")
                    if 'driver' not in drivers_dict[pos]:
                        # Chercher code 3 lettres dans le texte
                        pilot_match = re.search(r'([A-Za-z]{3})', next_text_clean)
                        if pilot_match:
                            pilot_candidate = pilot_match.group(1).upper()
                            if pilot_candidate in valid_drivers:
                                drivers_dict[pos]['driver'] = pilot_candidate
                                processed_indices.add(j)
                    
                    # Intervalle
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
                # Trouver la prochaine position libre
                while position_counter in drivers_dict:
                    position_counter += 1
                
                if position_counter <= 20:
                    drivers_dict[position_counter] = {
                        'position': position_counter,
                        'driver': pilot,
                        'interval': interval
                    }
                    processed_indices.add(i)
                    position_counter += 1
                i += 1
                continue
        
        # Cas 4 : Pilote seul
        if text in valid_drivers or text.upper() in valid_drivers:
            pilot = text.upper() if text.upper() in valid_drivers else text
            
            # Trouver la prochaine position libre
            while position_counter in drivers_dict:
                position_counter += 1
            
            if position_counter <= 20:
                drivers_dict[position_counter] = {'position': position_counter, 'driver': pilot}
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

def get_f1_data(image_path: str) -> List[Dict]:
    """
    Fonction principale
    """
    ocr_results = extract_text_from_image(image_path)
    drivers_data = parse_driver_data(ocr_results)
    return drivers_data

def save_data_to_dict(drivers_data: List[Dict]) -> Dict:
    """
    Transforme en dictionnaire structuré
    """
    return {
        "total_drivers": len(drivers_data),
        "drivers": drivers_data,
        "leader": drivers_data[0] if drivers_data else None
    }