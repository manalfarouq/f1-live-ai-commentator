import os
import re
import pdfplumber
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from app.core.config import settings


# ── Étape 1 : lire le PDF ────────────────────────────────────

def lire_pdf(chemin):
    """Ouvre le PDF et retourne tout le texte en une seule chaîne."""
    texte = ""
    with pdfplumber.open(chemin) as pdf:
        for page in pdf.pages:
            contenu = page.extract_text()
            if contenu:
                texte += contenu + "\n"
    return texte


# ── Étape 2 : découper en morceaux ───────────────────────────

def decouper(texte):
    """
    Découpe le texte en morceaux de CHUNK_SIZE caractères.
    Chaque morceau se chevauche de CHUNK_OVERLAP avec le suivant
    pour ne pas couper une règle en deux.
    """
    morceaux = []
    debut = 0

    while debut < len(texte):
        fin = debut + settings.CHUNK_SIZE

        # si on n'est pas à la fin, on coupe sur un saut de ligne
        if fin < len(texte):
            coupure = texte.rfind("\n", debut, fin)
            if coupure <= debut:
                coupure = fin
            fin = coupure

        morceau = texte[debut:fin].strip()
        if morceau:
            morceaux.append(morceau)

        # on recule un peu pour l'overlap
        debut = fin - settings.CHUNK_OVERLAP

    return morceaux


# ── Étape 3 : stocker dans ChromaDB ─────────────────────────

def indexer():
    """
    Pipeline complet :
    PDF → texte → morceaux → vecteurs → ChromaDB

    À appeler une seule fois au démarrage dans main.py.
    """

    # vérifie que le PDF existe
    if not os.path.exists(settings.F1_PDF_PATH):
        print(f"[RAG] PDF non trouvé : {settings.F1_PDF_PATH}")
        print("[RAG] → dépose f1_regles.pdf dans data/rag/ puis relance")
        return None

    # 1. lire
    print(f"[RAG] Lecture du PDF...")
    texte = lire_pdf(settings.F1_PDF_PATH)
    print(f"[RAG] {len(texte)} caractères extraits")

    # 2. découper
    print("[RAG] Découpage en morceaux...")
    morceaux = decouper(texte)
    print(f"[RAG] {len(morceaux)} morceaux créés")

    # 3. préparer le modèle d'embedding
    # SentenceTransformer transforme chaque morceau en vecteur de nombres.
    # Deux morceaux similaires auront des vecteurs proches → c'est ça la recherche vectorielle.
    print(f"[RAG] Chargement du modèle {settings.EMBED_MODEL}...")
    embedding_fn = SentenceTransformerEmbeddingFunction(
        model_name=settings.EMBED_MODEL,
        device="cpu"
    )

    # 4. créer la collection ChromaDB
    os.makedirs(settings.CHROMA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=settings.CHROMA_DIR)

    # on supprime l'ancienne collection si elle existe (pour repartir propre)
    try:
        client.delete_collection(settings.COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=settings.COLLECTION_NAME,
        embedding_function=embedding_fn
    )

    # 5. insérer les morceaux dans ChromaDB
    print("[RAG] Indexation dans ChromaDB...")
    ids = [f"chunk_{i}" for i in range(len(morceaux))]
    collection.add(documents=morceaux, ids=ids)

    print(f"[RAG] ✅ {len(morceaux)} morceaux indexés")
    return collection


if __name__ == "__main__":
    indexer()