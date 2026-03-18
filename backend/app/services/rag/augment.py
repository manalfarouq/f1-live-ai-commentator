# backend/app/services/rag/augment.py

import json
import time
from google import genai
from google.api_core.exceptions import ResourceExhausted

from app.core.config import settings
from app.services.rag.retriever import retriever, retriever_chat

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# ── Les 4 personas ───────────────────────────────────────────

PERSONAS = {
    "journaliste": "Tu es un commentateur F1 passionné et dramatique. Tu racontes la course comme une histoire.",
    "professeur" : "Tu es un prof qui explique la F1 simplement. Tu utilises des mots faciles pour les débutants.",
    "ingenieur"  : "Tu es un ingénieur de course. Tu analyses les stratégies et les données techniques.",
    "fan"        : "Tu es un fan de F1 très enthousiaste. Tu réagis avec émotion à chaque événement.",
}

# ── Cache anti-quota ──────────────────────────────────────────
# On ne génère un vrai commentaire que toutes les INTERVALLE_FRAMES frames
INTERVALLE_FRAMES = 10
_cache_rag = {persona: {"compteur": 0, "dernier": "Commentaire en attente..."} for persona in PERSONAS}


def _appeler_gemini(prompt: str, max_retries: int = 3) -> str:
    """Appelle Gemini avec retry automatique si quota dépassé (429)."""
    delai = 15

    for tentative in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text.strip()

        except ResourceExhausted:
            if tentative < max_retries - 1:
                print(f"⏳ RAG quota dépassé — attente {delai}s (tentative {tentative + 1}/{max_retries})")
                time.sleep(delai)
            else:
                print("❌ RAG quota dépassé — toutes les tentatives échouées")
                return None

        except Exception as e:
            print(f"❌ Erreur Gemini inattendue : {e}")
            return None


def generer_commentaire(race_data: dict, persona: str = "journaliste") -> dict:
    global _cache_rag

    if persona not in _cache_rag:
        _cache_rag[persona] = {"compteur": 0, "dernier": "Commentaire en attente..."}

    # Si on n'est pas sur un multiple de INTERVALLE_FRAMES → retourner le cache
    _cache_rag[persona]["compteur"] += 1
    if _cache_rag[persona]["compteur"] % INTERVALLE_FRAMES != 0:
        return {
            "commentaire": _cache_rag[persona]["dernier"],
            "persona"    : persona,
            "chunks"     : [],
        }

    chunks = retriever(race_data)

    contexte = ""
    for i, chunk in enumerate(chunks, 1):
        contexte += f"\n[Source {i}]\n{chunk['text']}\n"

    prompt = f"""{PERSONAS.get(persona, PERSONAS['journaliste'])}

DONNÉES DE LA COURSE :
{json.dumps(race_data, ensure_ascii=False, indent=2)}

CONTEXTE F1 :
{contexte}

INSTRUCTIONS :
- Écris un commentaire live en français.
- Utilise les données de course ET le contexte ci-dessus.
- 3 à 5 phrases maximum.
- Ne mentionne pas les mots "contexte" ou "source".

COMMENTAIRE :"""

    texte = _appeler_gemini(prompt)

    if texte:
        _cache_rag[persona]["dernier"] = texte
    else:
        texte = _cache_rag[persona]["dernier"]

    return {
        "commentaire": texte,
        "persona"    : persona,
        "chunks"     : chunks,
    }


def generer_tous_personas(race_data: dict) -> dict:
    return {
        persona: generer_commentaire(race_data, persona)
        for persona in PERSONAS
    }


def repondre_chat(question: str) -> dict:

    chunks   = retriever_chat(question)
    contexte = "\n\n".join(chunks)

    prompt = f"""Tu es un expert F1. Réponds à la question en utilisant uniquement le contexte ci-dessous.
Si la réponse n'est pas dans le contexte, dis-le honnêtement.

CONTEXTE :
{contexte}

QUESTION : {question}

RÉPONSE (2-3 phrases en français) :"""

    texte = _appeler_gemini(prompt)

    return {
        "question": question,
        "reponse" : texte or "Réponse indisponible (quota Gemini dépassé).",
    }