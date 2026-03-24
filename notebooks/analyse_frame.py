# notebooks/analyse_frame.py
#
# Ce fichier est le CHEF D'ORCHESTRE
# Il connecte tous tes fichiers existants :
#   ocr_extractor.py    → lire le texte dans l'image
#   lap_parser.py       → extraire le numéro de tour
#   indicator_detector.py → détecter les couleurs (violet, jaune, rouge)
#   team_mapper.py      → retrouver l'équipe d'un pilote
#
# Comment ça marche :
#   1. On reçoit une image (frame de la vidéo F1)
#   2. On lit tout le texte dedans (OCR)
#   3. On extrait les infos utiles (tour, pilotes, positions)
#   4. On détecte les indicateurs visuels
#   5. On retourne un dictionnaire propre avec toutes les infos

import re
from typing import Dict, List, Optional

# On importe tes fichiers existants
from ocr_extractor      import extract_text_from_image
from lap_parser         import extract_lap_info
from indicator_detector import detect_row_indicators
from team_mapper        import load_team_mapping_from_env


# Charger le mapping des équipes une seule fois au démarrage
TEAM_MAPPING = load_team_mapping_from_env()


def extraire_pilotes_depuis_ocr(ocr_results: List) -> List[Dict]:
    """
    Lit les résultats OCR et extrait les pilotes avec leur position et temps.

    Le texte OCR d'une image F1 ressemble à :
        "1  VER  1:32.456"
        "2  HAM  +0.823"
        "3  LEC  +1.234"

    On retourne une liste de dictionnaires :
        [
            {"position": 1, "pilote": "VER", "equipe": "Red Bull Racing", "temps": "1:32.456"},
            {"position": 2, "pilote": "HAM", "equipe": "Ferrari",         "temps": "+0.823"},
            ...
        ]
    """
    pilotes = []

    for (bbox, texte, proba) in ocr_results:
        texte = texte.strip()

        # On cherche les lignes qui commencent par un chiffre (= position)
        # Exemple : "3  LEC  +1.234"
        match = re.match(r'^(\d{1,2})\s+([A-Z]{2,4})', texte)

        if match:
            position = int(match.group(1))
            code_pilote = match.group(2)

            # Retrouver l'équipe depuis le code pilote
            equipe = TEAM_MAPPING.get(code_pilote, "Inconnu")

            # Extraire le temps s'il est présent dans le texte
            temps = ""
            match_temps = re.search(r'(\d+:\d+\.\d+|[+-]\d+\.\d+)', texte)
            if match_temps:
                temps = match_temps.group(1)

            pilotes.append({
                "position"  : position,
                "pilote"    : code_pilote,
                "equipe"    : equipe,
                "temps"     : temps,
            })

    # Trier par position
    pilotes.sort(key=lambda x: x["position"])
    return pilotes


def analyser_frame(image_path: str) -> Dict:
    """
    Fonction principale — analyse une image F1 complète.

    Étapes :
        1. Lire tout le texte de l'image (OCR)
        2. Extraire les infos de tour (LAP 23/58)
        3. Extraire la liste des pilotes et positions
        4. Détecter les indicateurs visuels (violet = fastest lap, jaune = warning)

    Retourne un dictionnaire avec toutes les infos de la frame.
    """

    # ── Étape 1 : Lire le texte dans l'image ──────────────────────
    print(f"Analyse de l'image : {image_path}")
    ocr_results = extract_text_from_image(image_path)
    print(f"  OCR : {len(ocr_results)} éléments de texte trouvés")


    # ── Étape 2 : Extraire les infos de tour ──────────────────────
    # lap_parser cherche "LAP 23 / 58" dans le texte OCR
    infos_tour = extract_lap_info(ocr_results)

    if infos_tour:
        print(f"  Tour : {infos_tour['current_lap']} / {infos_tour['total_laps']} ({infos_tour['progress_percentage']}%)")
    else:
        print("  Tour : non trouvé dans l'image")
        infos_tour = {"current_lap": 0, "total_laps": 0, "progress_percentage": 0.0}


    # ── Étape 3 : Extraire la liste des pilotes ───────────────────
    pilotes = extraire_pilotes_depuis_ocr(ocr_results)
    print(f"  Pilotes détectés : {len(pilotes)}")


    # ── Étape 4 : Détecter les indicateurs visuels ────────────────
    # indicator_detector regarde les couleurs à droite de chaque ligne
    indicateurs = detect_row_indicators(image_path, num_drivers=20)
    print(f"  Indicateurs : {indicateurs}")

    # Ajouter l'indicateur à chaque pilote
    for pilote in pilotes:
        pos = pilote["position"]
        pilote["indicateur"] = indicateurs.get(pos, None)


    # ── Résultat final ────────────────────────────────────────────
    resultat = {
        "tour"        : infos_tour,
        "pilotes"     : pilotes,
        "top3"        : pilotes[:3] if len(pilotes) >= 3 else pilotes,
        "nb_pilotes"  : len(pilotes),
    }

    return resultat


# ── Test rapide ───────────────────────────────────────────────────
# Lance ce fichier directement pour tester sur une image
# python analyse_frame.py

if __name__ == "__main__":
    import sys
    import json

    # Prendre le chemin de l'image en argument
    # Exemple : python analyse_frame.py ../data/frames/frame_001.jpg
    if len(sys.argv) < 2:
        print("Usage : python analyse_frame.py <chemin_image>")
        print("Exemple : python analyse_frame.py ../data/frames/frame_001.jpg")
    else:
        image_path = sys.argv[1]
        resultat = analyser_frame(image_path)

        print("\n=== RÉSULTAT ===")
        print(json.dumps(resultat, indent=2, ensure_ascii=False))