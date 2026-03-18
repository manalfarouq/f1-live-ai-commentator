# backend/app/services/analysis_service.py

import numpy as np
from app.services.ml_service  import predict
from app.services.llm_service import generate_commentary
from app.services.rag.augment import generer_commentaire


def analyser_frame(frame: np.ndarray, lap: int = 1, total_laps: int = 57) -> dict:
    """
    Analyse une frame vidéo et retourne les résultats complets.

    frame       → image numpy extraite par OpenCV
    lap         → tour actuel (extrait par OCR plus tard)
    total_laps  → nombre total de tours
    """

    # ── 1. Prédiction LightGBM ───────────────────────────────
    # on passe les données de base disponibles depuis la frame
    data_ml = {
        "lap"             : lap,
        "total_laps"      : total_laps,
        "current_position": 1,   # sera remplacé par OCR
        "grid_position"   : 1,
    }
    prediction = predict(data_ml)

    # ── 2. Commentaire LLM (ton llm_service existant) ────────
    predictions_list = [
        {"driver": "P1", "probability": prediction["probability"]},
        {"driver": "P2", "probability": max(prediction["probability"] - 20, 0)},
        {"driver": "P3", "probability": max(prediction["probability"] - 35, 0)},
    ]
    commentary_llm = generate_commentary(predictions_list)

    # ── 3. Commentaire RAG + Gemini ───────────────────────────
    race_data = {
        "event"      : "unknown",
        "lap"        : lap,
        "total_laps" : total_laps,
        "predictions": prediction,
    }
    commentary_rag = generer_commentaire(race_data, persona="journaliste")

    return {
        "lap"           : lap,
        "prediction"    : prediction,
        "commentary_llm": commentary_llm,
        "commentary_rag": commentary_rag["commentaire"],
    }