# backend/app/services/rag/augment.py

import json
import time
import math
from google import genai
from google.api_core.exceptions import ResourceExhausted

from app.core.config import settings
from app.services.rag.retriever import retriever, retriever_chat

client = genai.Client(api_key=settings.GEMINI_API_KEY)

PERSONAS = {
    "journaliste": "Tu es un commentateur F1 passionné et dramatique. Tu racontes la course comme une histoire.",
    "professeur" : "Tu es un prof qui explique la F1 simplement. Tu utilises des mots faciles pour les débutants.",
    "ingenieur"  : "Tu es un ingénieur de course. Tu analyses les stratégies et les données techniques.",
    "fan"        : "Tu es un fan de F1 très enthousiaste. Tu réagis avec émotion à chaque événement.",
}

# ── Quota disponible par service
QUOTA_PAR_SERVICE = 8   # 8 LLM + 8 RAG = 16 total, marge de sécurité

_cache_rag = {persona: {"compteur": 0, "dernier": "Commentaire en attente..."} for persona in PERSONAS}
_intervalle_rag = 10


def configurer_intervalle(nb_frames: int) -> int:
    """Calcule automatiquement l'intervalle pour rester sous le quota."""
    global _intervalle_rag
    _intervalle_rag = max(10, math.ceil(nb_frames / QUOTA_PAR_SERVICE))
    for persona in _cache_rag:
        _cache_rag[persona]["compteur"] = 0  # reset pour chaque nouvelle vidéo
    print(f"[RAG] {nb_frames} frames → INTERVALLE_FRAMES = {_intervalle_rag} (~{nb_frames // _intervalle_rag} appels Gemini)")
    return _intervalle_rag


def _appeler_gemini(prompt: str, max_retries: int = 3) -> str:
    delai = 15
    for tentative in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={"max_output_tokens": 80},
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
            if tentative < max_retries - 1:
                print(f"⏳ RAG erreur — attente {delai}s (tentative {tentative + 1}/{max_retries})")
                time.sleep(delai)
            else:
                print(f"❌ RAG toutes tentatives échouées : {e}")
                return None


def generer_commentaire(race_data: dict, persona: str = "journaliste") -> dict:
    global _cache_rag, _intervalle_rag

    if persona not in _cache_rag:
        _cache_rag[persona] = {"compteur": 0, "dernier": "Commentaire en attente..."}

    _cache_rag[persona]["compteur"] += 1
    if _cache_rag[persona]["compteur"] % _intervalle_rag != 0:
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
- MAXIMUM 2 phrases courtes, style oral.
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