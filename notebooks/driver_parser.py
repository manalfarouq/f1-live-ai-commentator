# notebooks/driver_parser.py

import re
from typing import List, Dict
from team_mapper import load_team_mapping_from_env, get_team_from_ocr_text

VALID_DRIVERS = {
    'VER', 'PIA', 'NOR', 'TSU', 'LEC', 'RUS', 'STR', 'ANT',
    'HAM', 'HUL', 'ALO', 'BOR', 'ALB', 'HAD', 'BEA', 'OCO',
    'SAI', 'GAS', 'COL', 'LAW', 'PER', 'ZHO', 'MAG', 'BOT',
    'LIN',
}

DRIVER_NAME_TO_CODE = {
    'VERSTAPPEN': 'VER', 'PIASTRI': 'PIA', 'NORRIS': 'NOR',
    'LECLERC': 'LEC', 'RUSSELL': 'RUS', 'ALONSO': 'ALO',
    'OCON': 'OCO', 'HAMILTON': 'HAM', 'BEARMAN': 'BEA',
    'STROLL': 'STR', 'HULKENBERG': 'HUL', 'BORTOLETO': 'BOR',
    'SAINZ': 'SAI', 'TSUNODA': 'TSU', 'ANTONELLI': 'ANT',
    'ALBON': 'ALB', 'HADJAR': 'HAD', 'LAWSON': 'LAW',
    'GASLY': 'GAS', 'COLAPINTO': 'COL', 'BOTTAS': 'BOT',
    'PEREZ': 'PER', 'LINDBLAD': 'LIN',
}

TEAM_MAPPING = load_team_mapping_from_env()

SPECIAL_STATUSES = {'out', 'in pit', 'dnf', 'dns', 'dsq', 'pit', 'inpit', 'in pit lane'}

CAR_NUMBERS = {
    '1', '2', '4', '5', '6', '7', '10', '11', '12', '14', '16',
    '18', '23', '27', '30', '31', '43', '44', '55', '63',
    '77', '81', '87'
}


def normalize_status(text: str) -> str:
    clean = re.sub(r'[^a-zA-Z ]', '', text).lower().strip()
    if re.match(r'in\s*p', clean):
        return 'in pit'
    if clean == 'out':
        return 'out'
    return clean


def fix_interval(interval: str) -> str:
    if not interval or not interval.startswith('+'):
        return interval
    match = re.match(r'\+(\d+)(\s*[A-Za-z].*)?$', interval.strip())
    if match:
        digits = match.group(1)
        suffix = match.group(2) or ''
        if '.' not in digits and len(digits) >= 2:
            return f"+{digits[:-1]}.{digits[-1]}{suffix}"
    return interval


def parse_driver_data(ocr_results: List) -> List[Dict]:
    sorted_results = sorted(ocr_results, key=lambda x: x[0][0][1])

    drivers_dict     = {}
    position_counter = 1
    processed_indices = set()

    i = 0
    while i < len(sorted_results):
        if i in processed_indices:
            i += 1
            continue

        bbox, text, prob = sorted_results[i]
        text      = text.strip()
        current_y = bbox[0][1]

        # ── Cas 1 : Position + pilote collés ("13 W ALB", "1 VERSTAPPEN") ───
        # Essaie d'abord avec nom complet
        match_full = re.match(r'^(\d{1,2})\s+([A-Z]{4,})$', text)
        if match_full:
            pos  = int(match_full.group(1))
            name = match_full.group(2)
            if 1 <= pos <= 22 and name in DRIVER_NAME_TO_CODE:
                pilot = DRIVER_NAME_TO_CODE[name]
                drivers_dict[pos] = {
                    'position': pos,
                    'driver'  : pilot,
                    'team'    : TEAM_MAPPING.get(pilot, 'Unknown'),
                }
                processed_indices.add(i)
                i += 1
                continue

        # Cas 1b : Position + code 3 lettres avec préfixe ("13 W ALB")
        match = re.match(r'^(\d{1,2})\s.*?([A-Z]{3})', text)
        if match:
            pos, pilot = int(match.group(1)), match.group(2)
            if 1 <= pos <= 22 and pilot in VALID_DRIVERS:
                team = get_team_from_ocr_text(text) or TEAM_MAPPING.get(pilot, 'Unknown')
                drivers_dict[pos] = {'position': pos, 'driver': pilot, 'team': team}
                processed_indices.add(i)

                interval_match = re.search(r'\+[\d.]+\s*[A-Za-z]', text)
                if interval_match:
                    drivers_dict[pos]['interval'] = fix_interval(interval_match.group(0))
                elif i + 1 < len(sorted_results):
                    _, next_text, _ = sorted_results[i + 1]
                    ns = normalize_status(next_text)
                    if ns in SPECIAL_STATUSES:
                        drivers_dict[pos]['interval'] = ns
                        processed_indices.add(i + 1)
                    elif '+' in next_text:
                        drivers_dict[pos]['interval'] = fix_interval(next_text.strip())
                        processed_indices.add(i + 1)

                i += 1
                continue

        # ── Cas 2 : Position seule ("10", "12") ─────────────────────────────
        if re.match(r'^\d{1,2}$', text):
            pos = int(text)
            if text in CAR_NUMBERS:
                i += 1
                continue
            if 1 <= pos <= 22 and pos not in drivers_dict:
                drivers_dict[pos] = {'position': pos}
                processed_indices.add(i)

                for j in range(i + 1, min(i + 5, len(sorted_results))):
                    if j in processed_indices:
                        continue
                    next_bbox, next_text, _ = sorted_results[j]
                    next_clean = next_text.strip()

                    if abs(next_bbox[0][1] - current_y) > 30:
                        break

                    if 'driver' not in drivers_dict[pos]:
                        # Nom complet
                        if next_clean.upper() in DRIVER_NAME_TO_CODE:
                            pilot = DRIVER_NAME_TO_CODE[next_clean.upper()]
                            drivers_dict[pos]['driver'] = pilot
                            drivers_dict[pos]['team']   = TEAM_MAPPING.get(pilot, 'Unknown')
                            processed_indices.add(j)
                        else:
                            pilot_match = re.search(r'([A-Za-z]{3})', next_clean)
                            if pilot_match:
                                candidate = pilot_match.group(1).upper()
                                if candidate in VALID_DRIVERS:
                                    drivers_dict[pos]['driver'] = candidate
                                    drivers_dict[pos]['team']   = TEAM_MAPPING.get(candidate, 'Unknown')
                                    processed_indices.add(j)

                    if 'interval' not in drivers_dict[pos]:
                        ns = normalize_status(next_clean)
                        if ns in SPECIAL_STATUSES:
                            drivers_dict[pos]['interval'] = ns
                            processed_indices.add(j)
                        elif '+' in next_clean or 'Interval' in next_clean:
                            drivers_dict[pos]['interval'] = fix_interval(next_clean)
                            processed_indices.add(j)

                i += 1
                continue

        # ── Cas 3 : Pilote code + reste ("NOR +24.645 H", "PIA Out") ────────
        match3 = re.match(r'^([A-Z]{3})\s+(.+)$', text)
        if match3:
            pilot = match3.group(1)
            rest  = match3.group(2).strip()
            if pilot in VALID_DRIVERS:
                while position_counter in drivers_dict:
                    position_counter += 1
                if position_counter <= 22:
                    ns = normalize_status(rest)
                    interval = ns if ns in SPECIAL_STATUSES else (fix_interval(rest) if rest.startswith('+') else rest)
                    drivers_dict[position_counter] = {
                        'position': position_counter,
                        'driver'  : pilot,
                        'team'    : TEAM_MAPPING.get(pilot, 'Unknown'),
                        'interval': interval,
                    }
                    processed_indices.add(i)
                    position_counter += 1
                i += 1
                continue

        # ── Cas 4 : Code 3 lettres seul ("VER", "Lec") ──────────────────────
        if text.upper() in VALID_DRIVERS:
            pilot = text.upper()
            while position_counter in drivers_dict:
                position_counter += 1
            if position_counter <= 22:
                drivers_dict[position_counter] = {
                    'position': position_counter,
                    'driver'  : pilot,
                    'team'    : TEAM_MAPPING.get(pilot, 'Unknown'),
                }
                processed_indices.add(i)

                if i + 1 < len(sorted_results) and (i + 1) not in processed_indices:
                    _, next_text, _ = sorted_results[i + 1]
                    ns = normalize_status(next_text)
                    if ns in SPECIAL_STATUSES:
                        drivers_dict[position_counter]['interval'] = ns
                        processed_indices.add(i + 1)
                    elif '+' in next_text or 'Interval' in next_text:
                        drivers_dict[position_counter]['interval'] = fix_interval(next_text.strip())
                        processed_indices.add(i + 1)

                position_counter += 1
                i += 1
                continue

        # ── Cas 4b : Nom complet seul ("VERSTAPPEN", "HAMILTON") ────────────
        if text.upper() in DRIVER_NAME_TO_CODE:
            pilot = DRIVER_NAME_TO_CODE[text.upper()]
            while position_counter in drivers_dict:
                position_counter += 1
            if position_counter <= 22:
                drivers_dict[position_counter] = {
                    'position': position_counter,
                    'driver'  : pilot,
                    'team'    : TEAM_MAPPING.get(pilot, 'Unknown'),
                }
                processed_indices.add(i)

                if i + 1 < len(sorted_results) and (i + 1) not in processed_indices:
                    _, next_text, _ = sorted_results[i + 1]
                    ns = normalize_status(next_text)
                    if ns in SPECIAL_STATUSES:
                        drivers_dict[position_counter]['interval'] = ns
                        processed_indices.add(i + 1)
                    elif '+' in next_text or 'Interval' in next_text:
                        drivers_dict[position_counter]['interval'] = fix_interval(next_text.strip())
                        processed_indices.add(i + 1)

                position_counter += 1

        i += 1

    return sorted(drivers_dict.values(), key=lambda x: x['position'])