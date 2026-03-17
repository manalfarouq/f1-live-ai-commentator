import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from app.core.config import settings


EVENEMENTS = {
    "flag_yellow"   : "drapeau jaune danger dépassement interdit règle",
    "flag_red"      : "drapeau rouge arrêt course session interrompue",
    "flag_blue"     : "drapeau bleu pilote doublé règle",
    "flag_green"    : "drapeau vert piste libre reprise course",
    "flag_black"    : "drapeau noir disqualification pilote",
    "flag_chequered": "drapeau damier fin course arrivée",
    "pit"           : "arrêt stands pit stop stratégie pneus",
    "safety_car"    : "voiture sécurité safety car SC règle déploiement",
    "vsc"           : "voiture sécurité virtuelle VSC ralentissement",
    "penalty"       : "pénalité infraction temps pilote règle",
    "dnf"           : "abandon DNF voiture arrêtée incident",
    "drs"           : "DRS aileron arrière dépassement règle écart",
    "fastest_lap"   : "meilleur tour fastest lap règle 2025",
    "tyre_soft"     : "pneu souple rouge performance Pirelli",
    "tyre_medium"   : "pneu medium jaune équilibre Pirelli",
    "tyre_hard"     : "pneu dur blanc durabilité Pirelli",
    "tyre_inter"    : "pneu intermédiaire vert pluie humide",
    "tyre_wet"      : "pneu pluie bleu forte pluie",
}


def construire_requete(race_data: dict) -> str:
    event     = race_data.get("event", "").lower()
    flag_type = race_data.get("flag_type", "").lower()
    tyre_type = race_data.get("tyre_type", "").lower()

    # ── détecte les phrases longues en anglais ───────────────
    # ex: "Safety Car deployed after a collision at Turn 1"
    if "safety car" in event:
        return EVENEMENTS["safety_car"]
    if "collision" in event or "accident" in event:
        return EVENEMENTS["safety_car"]
    if "pit" in event or "box" in event:
        return EVENEMENTS["pit"]
    if "yellow" in event:
        return EVENEMENTS["flag_yellow"]
    if "red flag" in event:
        return EVENEMENTS["flag_red"]
    # ─────────────────────────────────────────────────────────

    if event == "flag" and flag_type:
        cle = f"flag_{flag_type}"
    elif event == "tyre" and tyre_type:
        cle = f"tyre_{tyre_type}"
    else:
        cle = event

    return EVENEMENTS.get(cle, f"règle F1 {event}")


def _get_collection():
    """Ouvre la collection ChromaDB — mutualisé entre retriever et chat."""
    embedding_fn = SentenceTransformerEmbeddingFunction(
        model_name=settings.EMBED_MODEL,
        device="cpu"
    )
    client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
    return client.get_collection(
        name=settings.COLLECTION_NAME,
        embedding_function=embedding_fn
    )


def retriever(race_data: dict) -> list[dict]:
    requete    = construire_requete(race_data)
    collection = _get_collection()

    resultats = collection.query(
        query_texts=[requete],
        n_results=3,
        include=["documents", "distances"]
    )

    chunks = []
    for texte, distance in zip(
        resultats["documents"][0],
        resultats["distances"][0]
    ):
        score = round(1 / (1 + distance), 2)
        chunks.append({"text": texte, "score": score})

    return chunks


def retriever_chat(question: str) -> list[str]:
    collection = _get_collection()

    resultats = collection.query(
        query_texts=[question],
        n_results=3,
        include=["documents"]
    )

    return resultats["documents"][0]