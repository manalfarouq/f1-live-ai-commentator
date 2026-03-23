# backend/app/services/llm_service.py
import time
import math
from google import genai
from google.api_core.exceptions import ResourceExhausted
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

QUOTA_PAR_SERVICE = 8
_cache_llm = {"compteur": 0, "dernier": "Commentaire en attente...", "intervalle": 10}


def configurer_intervalle(nb_frames: int) -> int:
    intervalle = max(10, math.ceil(nb_frames / QUOTA_PAR_SERVICE))
    _cache_llm["intervalle"] = intervalle
    _cache_llm["compteur"]   = 0
    print(f"[LLM] {nb_frames} frames → INTERVALLE_FRAMES = {intervalle} (~{nb_frames // intervalle} appels Gemini)")
    return intervalle


def generate_commentary(
    predictions_list: list,
    lap: int = 0,
    total_laps: int = 0,
    position_predite: int = 0,
    probability: float = 0.0,
    max_retries: int = 3,
) -> str:
    global _cache_llm
    intervalle = _cache_llm["intervalle"]
    _cache_llm["compteur"] += 1

    if _cache_llm["compteur"] % intervalle != 0:
        return _cache_llm["dernier"]

    # Construire le contexte pilotes
    top3_lines = ""
    for i, p in enumerate(predictions_list[:3]):
        medals = ["1er", "2eme", "3eme"]
        driver = p.get("driver", f"P{i+1}")
        team   = p.get("team", "")
        prob   = p.get("probability", 0)
        team_str = f" ({team})" if team else ""
        top3_lines += f"  {medals[i]} : {driver}{team_str} — {prob:.1f}%\n"

    lap_str = f"Tour {lap}/{total_laps}" if lap and total_laps else "Début de course"
    ml_str  = f"Position {position_predite} ({probability:.1f}% de confiance)" if position_predite else "N/A"

    prompt = f"""Tu es un commentateur de Formule 1 passionné et dramatique.

DONNÉES DE LA COURSE :
- {lap_str}
- Prédiction ML : {ml_str}

CLASSEMENT ACTUEL (top 3) :
{top3_lines if top3_lines else "  Données en cours d'extraction..."}

CONSIGNES :
- MAXIMUM 2 phrases courtes, style commentateur TV oral
- Mentionne la prédiction ML ({ml_str}) dans ton commentaire
- PAS de markdown, PAS de **, texte brut uniquement
- Sois enthousiaste et dramatique
- Parle du classement et des enjeux"""

    delai = 15
    for tentative in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={"max_output_tokens": 80},  # ~2 phrases
            )
            _cache_llm["dernier"] = response.text
            return response.text
        except ResourceExhausted as e:
            if tentative < max_retries - 1:
                print(f"⏳ LLM erreur — attente {delai}s (tentative {tentative + 1}/{max_retries})")
                time.sleep(delai)
            else:
                err = str(e)
                print(f"❌ LLM toutes tentatives échouées : {err}")
                return f"Erreur lors de la génération du commentaire : {err}"
        except Exception as e:
            return f"Erreur lors de la génération du commentaire : {str(e)}"