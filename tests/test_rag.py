from app.services.rag.retriever import construire_requete, EVENEMENTS


def test_drapeau_jaune():
    result = construire_requete({"event": "flag", "flag_type": "yellow"})
    assert result == EVENEMENTS["flag_yellow"]


def test_safety_car():
    result = construire_requete({"event": "safety_car"})
    assert result == EVENEMENTS["safety_car"]


def test_pit():
    result = construire_requete({"event": "pit"})
    assert result == EVENEMENTS["pit"]


def test_phrase_anglaise():
    result = construire_requete({"event": "Safety Car deployed after collision"})
    assert result == EVENEMENTS["safety_car"]


def test_evenement_inconnu():
    result = construire_requete({"event": "inconnu"})
    assert "inconnu" in result