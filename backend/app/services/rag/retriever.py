# backend/app/services/rag/retriever.py
# ✅ CORRECTION : La collection est créée UNE SEULE FOIS au niveau module,
# pas à chaque appel de fonction. Gain de performance significatif.
from app.services.rag.indexer import get_collection

_collection = get_collection()


def retriever(question: str, n: int = 3) -> list[str]:
    """
    Recherche les n morceaux les plus pertinents pour une question.

    Args:
        question: La question ou requête texte
        n:        Nombre de morceaux à retourner (défaut : 3)

    Returns:
        Liste de textes pertinents
    """
    resultats = _collection.query(
        query_texts=[question],
        n_results=n,
        include=["documents"]
    )
    # resultats["documents"] est une liste de listes : [[doc1, doc2, doc3]]
    return resultats["documents"][0]