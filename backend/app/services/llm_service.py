# backend/app/services/llm_service.py
import time
import math
from google import genai
from google.api_core.exceptions import ResourceExhausted
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

QUOTA_PAR_SERVICE = 8
_cache_llm = {"compteur": 0, "dernier": "Commentaire en attente...", "intervalle": 10}
_fallback_idx = 0

EVENT_LABELS = {
    "fastest_lap": "FASTEST LAP vient d'être enregistré",
    "yellow_flag": "DRAPEAU JAUNE — danger sur la piste",
    "safety_car":  "SAFETY CAR déployée",
    "red_flag":    "DRAPEAU ROUGE — session arrêtée",
    "warning":     "AVERTISSEMENT détecté",
    "out":         "Pilote sorti de course",
    "in_pit":      "Pilote aux stands",
    "vsc":         "Virtual Safety Car active",
}


def _fallback_contextuel(predictions_list, lap, position_predite, probability, yolo_events):
    leader = predictions_list[0].get("driver", "P1") if predictions_list else "le leader"
    event_str = EVENT_LABELS.get(yolo_events[0], "") if yolo_events else ""

    templates = [
        f"{leader} maintient sa position — le modèle ML prédit P{position_predite} avec {probability:.0f}% de confiance, la course est loin d'être terminée !",
        f"Tour {lap} — tension maximale ! L'IA prédit une finition en P{position_predite}, {leader} doit gérer la pression.",
        f"{event_str + ' — ' if event_str else ''}{leader} en tête mais le classement peut tout basculer selon la stratégie.",
        f"Le modèle ML donne P{position_predite} à {probability:.0f}% — {leader} joue sa course sur ce tour crucial !",
    ]
    global _fallback_idx
    result = templates[_fallback_idx % len(templates)]
    _fallback_idx += 1
    return result


def configurer_intervalle(nb_frames: int) -> int:
    intervalle = max(10, math.ceil(nb_frames / QUOTA_PAR_SERVICE))
    _cache_llm["intervalle"] = intervalle
    _cache_llm["compteur"]   = 0
    print(f"[LLM] {nb_frames} frames → intervalle = {intervalle} (~{nb_frames // intervalle} appels Gemini)")
    return intervalle


def generate_commentary(
    predictions_list : list,
    lap              : int   = 0,
    total_laps       : int   = 0,
    position_predite : int   = 0,
    probability      : float = 0.0,
    yolo_events      : list  = None,
) -> str:
    yolo_events = yolo_events or []

    _cache_llm["compteur"] += 1
    if _cache_llm["compteur"] % _cache_llm["intervalle"] != 0:
        return _cache_llm["dernier"]

    # ── Contexte pilotes
    top3_lines = ""
    for i, p in enumerate(predictions_list[:3]):
        medals   = ["1er", "2ème", "3ème"]
        driver   = p.get("driver", f"P{i+1}")
        team     = p.get("team", "")
        prob     = p.get("probability", 0)
        team_str = f" ({team})" if team else ""
        top3_lines += f"  {medals[i]} : {driver}{team_str} — {prob:.1f}%\n"

    lap_str = f"Tour {lap}/{total_laps}" if lap and total_laps else "Début de course"
    ml_str  = f"Position {position_predite} ({probability:.1f}% de confiance)" if position_predite else "N/A"

    # ── Contexte YOLO events
    events_str = ""
    if yolo_events:
        labels = [EVENT_LABELS.get(e, e.upper()) for e in yolo_events]
        events_str = f"\nÉVÉNEMENTS YOLO DÉTECTÉS : {' | '.join(labels)}"

    prompt = f"""Tu es un commentateur F1 TV en direct, style Canal+.

DONNÉES COURSE :
- {lap_str}
- Prédiction ML : {ml_str}

CLASSEMENT :
{top3_lines if top3_lines else "  Extraction en cours..."}
{events_str}

CONSIGNES STRICTES :
- UNE ou DEUX phrases complètes, minimum 15 mots chacune
- Si un événement YOLO est détecté, mentionne-le explicitement
- Cite le nom d'un pilote du classement
- Mentionne la prédiction ML (position ou probabilité)
- Texte brut, pas de markdown, pas de **"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"max_output_tokens": 160},
        )
        result = response.text.strip()

    except ResourceExhausted:
        print("[LLM] Quota Gemini atteint — fallback contextuel")
        result = _fallback_contextuel(predictions_list, lap, position_predite, probability, yolo_events)

    except Exception as e:
        print(f"[LLM] Erreur : {e}")
        result = _fallback_contextuel(predictions_list, lap, position_predite, probability, yolo_events)

    _cache_llm["dernier"] = result
    return result