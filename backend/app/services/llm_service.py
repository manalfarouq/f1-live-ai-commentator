# backend/app/services/llm_service.py

import time
from google import genai
from google.api_core.exceptions import ResourceExhausted
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ── Cache anti-quota ──────────────────────────────────────────
# On ne génère un vrai commentaire que toutes les INTERVALLE_FRAMES frames
INTERVALLE_FRAMES = 10
_cache_llm = {"compteur": 0, "dernier": "Commentaire en attente..."}


def generate_commentary(predictions_list, max_retries: int = 3) -> str:
    global _cache_llm

    # Si on n'est pas sur un multiple de INTERVALLE_FRAMES → retourner le cache
    _cache_llm["compteur"] += 1
    if _cache_llm["compteur"] % INTERVALLE_FRAMES != 0:
        return _cache_llm["dernier"]

    prompt = f"""Tu es un commentateur de Formule 1 passionné. 

Voici les prédictions du Top 3 pour cette course :

🥇 1er : {predictions_list[0]['driver']} ({predictions_list[0]['probability']:.1f}% de chances)
🥈 2ème : {predictions_list[1]['driver']} ({predictions_list[1]['probability']:.1f}% de chances)
🥉 3ème : {predictions_list[2]['driver']} ({predictions_list[2]['probability']:.1f}% de chances)

Génère un commentaire court (2-3 phrases) et enthousiaste sur ce podium prédit."""

    delai = 15

    for tentative in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            _cache_llm["dernier"] = response.text
            return response.text

        except ResourceExhausted:
            if tentative < max_retries - 1:
                print(f"⏳ LLM quota dépassé — attente {delai}s (tentative {tentative + 1}/{max_retries})")
                time.sleep(delai)
            else:
                print("❌ LLM quota dépassé — commentaire mis en cache")
                return _cache_llm["dernier"]

        except Exception as e:
            return f"Erreur lors de la génération du commentaire : {str(e)}"

    return _cache_llm["dernier"]