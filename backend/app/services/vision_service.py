# backend/app/services/vision_service.py

import re
import cv2
import easyocr
from pathlib import Path
from typing import Dict, List, Optional
from ultralytics import YOLO

MODEL_DIR  = Path(__file__).resolve().parents[2] / "models"
YOLO_MODEL = MODEL_DIR / "yolo_f1_indicators.pt"

YOLO_TO_INDICATOR = {
    "purple stopwatch icon":   "fastest_lap",
    "Yellow exclamation mark": "warning",
    "Red exclamation mark":    "danger",
    "Yellow flag":             "yellow_flag",
    "Red flag":                "red_flag",
    "Green flag":              "green_flag",
    "Safety Car":              "safety_car",
    "Virtual Safety Car":      "vsc",
    "in pit":                  "in_pit",
    "out":                     "out",
    "Checkered":               "checkered",
    "VSC ending":              "vsc_ending",
}

TEAM_MAP = {
    "VER":"Red Bull","PER":"Red Bull","LEC":"Ferrari","SAI":"Ferrari",
    "HAM":"Mercedes","RUS":"Mercedes","NOR":"McLaren","PIA":"McLaren",
    "ALO":"Aston Martin","STR":"Aston Martin","GAS":"Alpine","OCO":"Alpine",
    "ALB":"Williams","SAR":"Williams","TSU":"AlphaTauri","RIC":"AlphaTauri",
    "ZHO":"Alfa Romeo","BOT":"Alfa Romeo","MAG":"Haas","HUL":"Haas",
    "BEA":"Haas","DOO":"Alpine","LAW":"AlphaTauri","ANT":"Mercedes",
}

_ocr_reader: Optional[easyocr.Reader] = None
_yolo_model: Optional[YOLO]           = None

def _get_ocr() -> easyocr.Reader:
    global _ocr_reader
    if _ocr_reader is None:
        print("[VISION] Chargement EasyOCR...")
        _ocr_reader = easyocr.Reader(['en'], gpu=False)
        print("[VISION] ✅ EasyOCR prêt")
    return _ocr_reader

def _get_yolo() -> Optional[YOLO]:
    global _yolo_model
    if _yolo_model is None:
        if YOLO_MODEL.exists():
            print(f"[VISION] Chargement YOLO depuis {YOLO_MODEL}...")
            _yolo_model = YOLO(str(YOLO_MODEL))
            print("[VISION] ✅ YOLO prêt")
        else:
            print(f"[VISION] ⚠ Modèle YOLO introuvable : {YOLO_MODEL}")
    return _yolo_model

# ── Crop leaderboard (bande gauche, ~25% largeur) ─────────────────────────────
def _crop_leaderboard(image: cv2.Mat) -> cv2.Mat:
    """
    Le leaderboard F1 TV occupe toujours la bande gauche.
    On isole cette zone pour réduire le bruit OCR.
    """
    h, w = image.shape[:2]
    # bande gauche 28%, toute la hauteur sauf les 10% bas (ticker)
    return image[0:int(h * 0.90), 0:int(w * 0.28)]

# ── OCR sur le crop leaderboard ───────────────────────────────────────────────
def _extraire_texte(image_path: str):
    reader = _get_ocr()
    image  = cv2.imread(image_path)
    if image is None:
        return [], None
    crop = _crop_leaderboard(image)
    results = reader.readtext(crop, detail=1, paragraph=False)
    return results, crop

# ── Regrouper les boîtes OCR par ligne (même Y ± tolérance) ──────────────────
def _grouper_par_ligne(ocr_results: List, tolerance_y: int = 12) -> List[List]:
    """
    EasyOCR retourne une bbox par mot. On regroupe les mots
    dont le centre Y est proche (même ligne de leaderboard).
    Retourne : [[mot1, mot2, ...], [mot1, mot2, ...], ...]
    Chaque mot = (bbox, texte, conf)
    """
    if not ocr_results:
        return []

    # centre Y de chaque bbox
    def centre_y(item):
        bbox = item[0]
        ys = [pt[1] for pt in bbox]
        return sum(ys) / len(ys)

    def centre_x(item):
        bbox = item[0]
        xs = [pt[0] for pt in bbox]
        return sum(xs) / len(xs)

    # trier par Y
    tries = sorted(ocr_results, key=centre_y)

    lignes = []
    ligne_courante = [tries[0]]
    y_ref = centre_y(tries[0])

    for item in tries[1:]:
        if abs(centre_y(item) - y_ref) <= tolerance_y:
            ligne_courante.append(item)
        else:
            lignes.append(sorted(ligne_courante, key=centre_x))
            ligne_courante = [item]
            y_ref = centre_y(item)
    lignes.append(sorted(ligne_courante, key=centre_x))

    return lignes

# ── Extraction pilotes depuis les lignes regroupées ───────────────────────────
def _extraire_pilotes(ocr_results: List) -> List[Dict]:
    """
    Stratégie : on regroupe d'abord les bboxes par ligne,
    puis on cherche dans chaque ligne : un numéro + un code 3 lettres.
    Ça fonctionne même si position / code / temps sont dans des bboxes séparées.
    """
    lignes = _grouper_par_ligne(ocr_results)
    pilotes = []

    for ligne in lignes:
        textes = [item[1].strip() for item in ligne]
        ligne_str = " ".join(textes)

        # cherche un numéro de position (1-20)
        pos_match = re.search(r'\b(\d{1,2})\b', ligne_str)
        # cherche un code pilote 2-4 lettres majuscules connu
        code_match = re.search(r'\b([A-Z]{2,4})\b', ligne_str)

        if not pos_match or not code_match:
            continue

        position    = int(pos_match.group(1))
        code_pilote = code_match.group(1)

        # filtre les faux positifs (codes inconnus = bruit OCR)
        if code_pilote not in TEAM_MAP:
            continue
        if position < 1 or position > 20:
            continue

        equipe = TEAM_MAP.get(code_pilote, "Unknown")

        # cherche un intervalle/temps dans la ligne
        interval = ""
        t_match = re.search(r'([+-]?\d+\.\d+|\d+:\d+\.\d+)', ligne_str)
        if t_match:
            interval = t_match.group(1)

        pilotes.append({
            "position": position,
            "code":     code_pilote,
            "name":     code_pilote,
            "team":     equipe,
            "interval": interval if interval else ("LEADER" if position == 1 else ""),
        })

    # dédoublonner par position (garder le premier match)
    seen = set()
    unique = []
    for p in sorted(pilotes, key=lambda x: x["position"]):
        if p["position"] not in seen:
            seen.add(p["position"])
            unique.append(p)

    return unique

# ── Extraction infos de tour ──────────────────────────────────────────────────
def _extraire_tour(ocr_results: List) -> Dict:
    for (_, texte, _) in ocr_results:
        m = re.search(r'(?:LAP|Lap)\s+(\d+)\s*[/of]\s*(\d+)', texte, re.I)
        if m:
            return {
                "current_lap": int(m.group(1)),
                "total_laps":  int(m.group(2)),
            }
    return {"current_lap": 0, "total_laps": 0}

# ── Détection indicateurs YOLO ────────────────────────────────────────────────
def _detecter_indicateurs(image_path: str) -> Dict[str, bool]:
    model = _get_yolo()
    if model is None:
        return {}
    try:
        results    = model(image_path, verbose=False)
        indicators = {}
        for result in results:
            for box in result.boxes:
                class_name = result.names[int(box.cls)]
                if class_name in YOLO_TO_INDICATOR:
                    indicators[YOLO_TO_INDICATOR[class_name]] = True
        return indicators
    except Exception as e:
        print(f"[VISION] ⚠ Erreur YOLO : {e}")
        return {}

# ── Fonction principale ───────────────────────────────────────────────────────
def analyser_frame(image_path: str) -> Dict:
    ocr_results, _ = _extraire_texte(image_path)
    drivers         = _extraire_pilotes(ocr_results)
    lap_info        = _extraire_tour(ocr_results)
    indicators      = _detecter_indicateurs(image_path)
    events          = [k for k, v in indicators.items() if v]

    return {
        "drivers"   : drivers,
        "indicators": indicators,
        "events"    : events,
        "lap_info"  : lap_info,
        "top3"      : drivers[:3] if len(drivers) >= 3 else drivers,
    }