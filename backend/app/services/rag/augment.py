# backend/app/services/rag/augment.py
from google import genai
from app.core.config import settings
from app.services.rag.retriever import retriever

client = genai.Client(api_key=settings.GEMINI_API_KEY)

PERSONAS = {
    "journaliste": "Tu es un commentateur F1 passionné et dramatique. Tu racontes la course comme une histoire.",
    "professeur" : "Tu es un prof qui explique la F1 simplement, avec des mots faciles pour les débutants.",
    "ingenieur"  : "Tu es un ingénieur de course. Tu analyses les stratégies et les données techniques.",
    "fan"        : "Tu es un fan de F1 très enthousiaste. Tu réagis avec émotion à chaque événement.",
}


# ─── Chat RAG (question → PDF → réponse) ──────────────────────────────────────

def repondre_chat(question: str) -> dict:
    """Flow RAG simple : question → chunks PDF → Gemini → réponse."""
    chunks = retriever(question)
    contexte = "\n\n".join(chunks) if chunks else "Aucun contexte disponible."

    prompt = f"""Tu es un expert en Formula 1.

Contexte :
{contexte}

Question : {question}

Instructions :
- Réponds clairement et simplement
- Utilise le contexte en priorité
- Si le contexte n'est pas suffisant, utilise tes connaissances générales
- Réponse courte (2 à 4 phrases)
- N'invente pas d'informations

Réponse :"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"max_output_tokens": 200},
        )
        answer = response.text.strip()
    except Exception as e:
        print(f"[RAG] Erreur Gemini chat : {e}")
        answer = "Désolé, je ne peux pas répondre pour le moment."

    return {"question": question, "answer": answer}


# ─── Commentaire live (race_data → PDF → persona → commentaire) ───────────────

def generer_commentaire(race_data: dict, persona: str = "journaliste") -> dict:
    """Génère un commentaire de course selon le persona choisi."""
    import json

    # Construit une requête lisible pour le retriever
    question = f"{race_data.get('event', '')} {race_data.get('flag_type', '')} {race_data.get('tyre_type', '')}"
    chunks = retriever(question.strip() or "règle F1 course")
    contexte = "\n\n".join(chunks) if chunks else "Aucun contexte disponible."

    prompt = f"""{PERSONAS.get(persona, PERSONAS['journaliste'])}

Données de course : {json.dumps(race_data, ensure_ascii=False)}

Contexte réglementaire :
{contexte}

Instructions : 2 phrases maximum, français, style oral, pas de markdown.

Commentaire :"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"max_output_tokens": 80},
        )
        texte = response.text.strip()
    except Exception as e:
        print(f"[RAG] Erreur Gemini commentaire : {e}")
        texte = "La course continue, restez connectés !"

    return {"commentaire": texte, "persona": persona}


def generer_tous_personas(race_data: dict) -> dict:
    """Génère un commentaire pour chaque persona."""
    return {p: generer_commentaire(race_data, p) for p in PERSONAS}

# ─── Quota / intervalle (utilisé par video_service) ───────────────────────────

def configurer_intervalle(nb_frames: int) -> int:
    """
    Calcule combien de frames attendre entre deux appels RAG.
    Evite de spammer Gemini sur une vidéo longue.
    Ex: 40 frames → intervalle de 5 (appel toutes les 5 frames)
    """
    import math
    QUOTA_PAR_SERVICE = 8
    return max(5, math.ceil(nb_frames / QUOTA_PAR_SERVICE))