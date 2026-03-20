# backend/app/services/video_service.py
#
# Ce fichier fait 3 choses simples :
#   1. Sauvegarder la vidéo uploadée
#   2. Extraire les frames avec OpenCV
#   3. Analyser chaque frame (ML + LLM + RAG + Vision)

import os
import cv2
import uuid

from app.services.ml_service       import predict
from app.services.llm_service      import generate_commentary, configurer_intervalle as llm_config
from app.services.rag.augment      import generer_commentaire, configurer_intervalle as rag_config
from app.services.analysis_service   import analyser_frame as vision_analyser_frame

# Dossier où on sauvegarde les vidéos uploadées
UPLOAD_DIR = "/tmp/f1_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── 1. Sauvegarder la vidéo ───────────────────────────────────────────────────

def sauvegarder_video(contenu: bytes, nom: str) -> str:
    """Sauvegarde les bytes de la vidéo sur le disque. Retourne le chemin."""
    chemin = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}_{nom}")
    with open(chemin, "wb") as f:
        f.write(contenu)
    return chemin


# ── 2. Extraire les frames ────────────────────────────────────────────────────

def extraire_frames(chemin_video: str, intervalle_secondes: int = 2) -> list:
    """
    Extrait une frame toutes les X secondes.
    Retourne une liste de {"frame": chemin_image, "timestamp": secondes}
    """
    cap    = cv2.VideoCapture(chemin_video)
    fps    = cap.get(cv2.CAP_PROP_FPS) or 25
    frames = []
    frame_idx = 0

    while True:
        ok, image = cap.read()
        if not ok:
            break

        # On garde seulement 1 frame toutes les X secondes
        if frame_idx % int(fps * intervalle_secondes) == 0:     
            timestamp    = int(frame_idx / fps)
            chemin_frame = os.path.join(UPLOAD_DIR, f"frame_{frame_idx}.jpg")
            cv2.imwrite(chemin_frame, image)
            frames.append({"frame": chemin_frame, "timestamp": timestamp})

        frame_idx += 1

    cap.release()
    return frames


# ── 3. Analyser une frame ─────────────────────────────────────────────────────

def analyser_frame(frame: str, lap: int, total_laps: int) -> dict:
    """
    Analyse une frame et retourne toutes les infos :
      - prediction ML
      - commentaire LLM
      - commentaire RAG
      - vision (YOLO + OCR) : pilotes, indicateurs, tour
    """

    # ── Vision : YOLO + OCR ──────────────────────────────────────
    vision = vision_analyser_frame(frame)

    # ── ML : prédiction position ──────────────────────────────────
    race_data = {
        "lap"        : lap,
        "total_laps" : total_laps,
        "drivers"    : vision.get("drivers", []),
        "indicators" : vision.get("indicators", {}),
    }
    prediction = predict(race_data)

    # ── LLM : commentaire général ─────────────────────────────────
    top3 = vision.get("top3", [])
    predictions_list = [
        {"driver": p.get("driver", "?"), "probability": prediction.get("probability", 50)}
        for p in top3
    ] or [{"driver": "P1", "probability": 50},
          {"driver": "P2", "probability": 30},
          {"driver": "P3", "probability": 20}]

    commentary_llm = generate_commentary(predictions_list)

    # ── RAG : commentaire journaliste ─────────────────────────────
    commentary_rag = generer_commentaire(race_data, persona="journaliste")
    commentary_rag = commentary_rag.get("commentaire", "")

    return {
    "lap"           : lap,
    "drivers"       : vision.get("drivers", []),
    "indicators"    : vision.get("indicators", {}),
    "events"        : vision.get("events", []),
    "prediction"    : prediction,
    "commentary_llm": commentary_llm,
    "commentary_rag": commentary_rag,
}


# ── 4. Configurer le throttling Gemini avant de lancer l'analyse ──────────────

def configurer_quota(nb_frames: int):
    """
    Calcule automatiquement l'intervalle Gemini selon le nombre de frames.
    À appeler une fois avant la boucle d'analyse.
    """
    llm_config(nb_frames)
    rag_config(nb_frames)