# notebooks/driver_parser.py

import re
from typing import List, Dict
from team_mapper import load_team_mapping_from_env, get_team_from_ocr_text

VALID_DRIVERS = {
    'VER', 'PIA', 'NOR', 'TSU', 'LEC', 'RUS', 'STR', 'ANT',
    'HAM', 'HUL', 'ALO', 'BOR', 'ALB', 'HAD', 'BEA', 'OCO',
    'SAI', 'GAS', 'COL', 'LAW', 'PER', 'ZHO', 'MAG', 'BOT'
}

# Chargé une seule fois au démarrage depuis le .env
TEAM_MAPPING = load_team_mapping_from_env()


def parse_driver_data(ocr_results: List) -> List[Dict]:
    """
    Parse les résultats OCR pour extraire position, pilote, équipe, intervalle

    4 cas gérés :
    - Cas 1 : Position + pilote collés  ("13 W ALB", "20 P8 LAW +10.431 H")
    - Cas 2 : Position seule            ("10", "12", "15")
    - Cas 3 : Pilote + intervalle       ("NOR +24.645 H")
    - Cas 4 : Pilote seul               ("VER", "HAM", "Lec")
    """
    sorted_results = sorted(ocr_results, key=lambda x: x[0][0][1])

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

        # Cas 1 : Position + pilote ("13 W ALB", "20 P8 LAW +10.431 H")
        match = re.match(r'^(\d{1,2})\s.*?([A-Z]{3})', text)
        if match:
            pos, pilot = int(match.group(1)), match.group(2)
            if 1 <= pos <= 20 and pilot in VALID_DRIVERS:
                team = get_team_from_ocr_text(text) or TEAM_MAPPING.get(pilot, 'Unknown')
                drivers_dict[pos] = {'position': pos, 'driver': pilot, 'team': team}
                processed_indices.add(i)

                interval_match = re.search(r'\+[\d.]+\s*H', text)
                if interval_match:
                    drivers_dict[pos]['interval'] = interval_match.group(0)
                elif i + 1 < len(sorted_results):
                    _, next_text, _ = sorted_results[i + 1]
                    if '+' in next_text:
                        drivers_dict[pos]['interval'] = next_text
                        processed_indices.add(i + 1)

                i += 1
                continue

        # Cas 2 : Position seule ("10", "12")
        if re.match(r'^\d{1,2}$', text):
            pos = int(text)
            if 1 <= pos <= 20 and pos not in drivers_dict:
                drivers_dict[pos] = {'position': pos}
                processed_indices.add(i)

                for j in range(i + 1, min(i + 4, len(sorted_results))):
                    if j in processed_indices:
                        continue

                    next_bbox, next_text, _ = sorted_results[j]
                    next_text_clean = next_text.strip()

                    if abs(next_bbox[0][1] - current_y) > 20:
                        break

                    # Chercher pilote
                    if 'driver' not in drivers_dict[pos]:
                        pilot_match = re.search(r'([A-Za-z]{3})', next_text_clean)
                        if pilot_match:
                            candidate = pilot_match.group(1).upper()
                            if candidate in VALID_DRIVERS:
                                drivers_dict[pos]['driver'] = candidate
                                drivers_dict[pos]['team'] = TEAM_MAPPING.get(candidate, 'Unknown')
                                processed_indices.add(j)

                    # Chercher intervalle
                    if 'interval' not in drivers_dict[pos] and ('+' in next_text_clean or 'Interval' in next_text_clean):
                        drivers_dict[pos]['interval'] = next_text_clean
                        processed_indices.add(j)

                i += 1
                continue

        # Cas 3 : Pilote + intervalle ("NOR +24.645 H")
        match = re.match(r'^([A-Z]{3})\s(\+[\d.]+\s*H)', text)
        if match:
            pilot, interval = match.group(1), match.group(2)
            if pilot in VALID_DRIVERS:
                while position_counter in drivers_dict:
                    position_counter += 1
                if position_counter <= 20:
                    drivers_dict[position_counter] = {
                        'position': position_counter,
                        'driver': pilot,
                        'team': TEAM_MAPPING.get(pilot, 'Unknown'),
                        'interval': interval
                    }
                    processed_indices.add(i)
                    position_counter += 1
                i += 1
                continue

        # Cas 4 : Pilote seul ("VER", "Lec", "OcO")
        if text in VALID_DRIVERS or text.upper() in VALID_DRIVERS:
            pilot = text.upper() if text.upper() in VALID_DRIVERS else text
            while position_counter in drivers_dict:
                position_counter += 1

            if position_counter <= 20:
                drivers_dict[position_counter] = {
                    'position': position_counter,
                    'driver': pilot,
                    'team': TEAM_MAPPING.get(pilot, 'Unknown')
                }
                processed_indices.add(i)

                if i + 1 < len(sorted_results) and (i + 1) not in processed_indices:
                    _, next_text, _ = sorted_results[i + 1]
                    if '+' in next_text or 'Interval' in next_text:
                        drivers_dict[position_counter]['interval'] = next_text
                        processed_indices.add(i + 1)

                position_counter += 1

        i += 1

    return sorted(drivers_dict.values(), key=lambda x: x['position'])