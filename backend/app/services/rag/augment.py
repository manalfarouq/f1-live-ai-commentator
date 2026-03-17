import json
from google import genai

from app.core.config import settings
from app.services.rag.retriever import retriever, retriever_chat

# client créé une seule fois ici — pas dans chaque fonction
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# ── Les 4 personas ───────────────────────────────────────────

PERSONAS = {
    "journaliste": "Tu es un commentateur F1 passionné et dramatique. Tu racontes la course comme une histoire.",
    "professeur" : "Tu es un prof qui explique la F1 simplement. Tu utilises des mots faciles pour les débutants.",
    "ingenieur"  : "Tu es un ingénieur de course. Tu analyses les stratégies et les données techniques.",
    "fan"        : "Tu es un fan de F1 très enthousiaste. Tu réagis avec émotion à chaque événement.",
}


def _appeler_gemini(prompt: str) -> str:
    """Appelle Gemini avec la nouvelle syntaxe google.genai."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text.strip()


def generer_commentaire(race_data: dict, persona: str = "journaliste") -> dict:

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

    return {
        "commentaire": _appeler_gemini(prompt),
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

    return {
        "question": question,
        "reponse" : _appeler_gemini(prompt),
    }