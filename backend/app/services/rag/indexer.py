# backend/app/services/rag/indexer.py
import os
import pdfplumber
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from app.core.config import settings


def lire_pdf(chemin: str) -> str:
    """Lit le PDF et retourne tout le texte."""
    texte = ""
    with pdfplumber.open(chemin) as pdf:
        for page in pdf.pages:
            contenu = page.extract_text()
            if contenu:
                texte += contenu + "\n"
    return texte


def decouper(texte: str) -> list[str]:
    """Découpe le texte en morceaux avec chevauchement."""
    morceaux = []
    debut = 0
    while debut < len(texte):
        fin = debut + settings.CHUNK_SIZE
        if fin < len(texte):
            coupure = texte.rfind("\n", debut, fin)
            fin = coupure if coupure > debut else fin
        morceau = texte[debut:fin].strip()
        if morceau:
            morceaux.append(morceau)
        debut = fin - settings.CHUNK_OVERLAP
    return morceaux


# ✅ CORRECTION : Collection initialisée une seule fois au démarrage,
# pas à chaque requête (voir retriever.py)
def get_collection():
    """Retourne la collection ChromaDB (connexion partagée)."""
    embedding_fn = SentenceTransformerEmbeddingFunction(
        model_name=settings.EMBED_MODEL,
        device="cpu"
    )
    os.makedirs(settings.CHROMA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
    return client.get_or_create_collection(
        name=settings.COLLECTION_NAME,
        embedding_function=embedding_fn
    )


def indexer():
    """
    PDF → texte → morceaux → ChromaDB.
    Si déjà indexé, ne fait rien (idempotent).
    """
    if not os.path.exists(settings.F1_PDF_PATH):
        print(f"[RAG] PDF introuvable : {settings.F1_PDF_PATH}")
        print("[RAG] → dépose f1_regles.pdf dans data/rag/ et relance")
        return None

    collection = get_collection()

    if collection.count() > 0:
        print(f"[RAG] Déjà indexé ({collection.count()} chunks) ✅")
        return collection

    print("[RAG] Lecture du PDF...")
    texte = lire_pdf(settings.F1_PDF_PATH)
    print(f"[RAG] {len(texte)} caractères extraits")

    morceaux = decouper(texte)
    print(f"[RAG] {len(morceaux)} morceaux créés")

    ids = [f"chunk_{i}" for i in range(len(morceaux))]
    collection.add(documents=morceaux, ids=ids)
    print(f"[RAG] ✅ {len(morceaux)} morceaux indexés")

    return collection