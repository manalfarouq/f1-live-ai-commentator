# backend/app/services/rag/retriever.py

# ── PAS d'import de indexer ici ──────────────────────────────────────────────
_collection = None

# ── Dictionnaire des requêtes par événement F1 ────────────────────────────────
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
    """Construit une requête textuelle à partir des données de course."""
    event     = race_data.get("event", "").lower()
    flag_type = race_data.get("flag_type", "").lower()
    tyre_type = race_data.get("tyre_type", "").lower()

    # Détecte les phrases longues en anglais
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

    # Événements structurés
    if event == "flag" and flag_type:
        cle = f"flag_{flag_type}"
    elif event == "tyre" and tyre_type:
        cle = f"tyre_{tyre_type}"
    else:
        cle = event

    return EVENEMENTS.get(cle, f"règle F1 {event}")


def retriever(question: str, n: int = 3) -> list[str]:
    """Recherche les n morceaux les plus pertinents pour une question."""
    global _collection
    if _collection is None:
        from app.services.rag.indexer import get_collection  # ← import ici
        _collection = get_collection()

    resultats = _collection.query(
        query_texts=[question],
        n_results=n,
        include=["documents"]
    )
    return resultats["documents"][0]