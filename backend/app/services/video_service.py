# backend/app/services/video_service.py

import os
import cv2
import uuid

from app.services.ml_service       import predict
from app.services.llm_service      import generate_commentary, configurer_intervalle as llm_config
from app.services.rag.augment      import generer_commentaire, configurer_intervalle as rag_config
from app.services.vision_service   import analyser_frame as vision_analyser_frame

UPLOAD_DIR = "/tmp/f1_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def sauvegarder_video(contenu: bytes, nom: str) -> str:
    chemin = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}_{nom}")
    with open(chemin, "wb") as f:
        f.write(contenu)
    return chemin


def extraire_frames(chemin_video: str, intervalle_secondes: int = 2) -> list:
    cap = cv2.VideoCapture(chemin_video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frames = []
    frame_idx = 0
    while True:
        ok, image = cap.read()
        if not ok:
            break
        if frame_idx % int(fps * intervalle_secondes) == 0:
            timestamp    = int(frame_idx / fps)
            chemin_frame = os.path.join(UPLOAD_DIR, f"frame_{frame_idx}.jpg")
            cv2.imwrite(chemin_frame, image)
            frames.append({"frame": chemin_frame, "timestamp": timestamp})
        frame_idx += 1
    cap.release()
    return frames


def analyser_frame(frame: str, lap: int, total_laps: int) -> dict:
    # 1. Vision OCR + YOLO
    vision     = vision_analyser_frame(frame)
    drivers    = vision.get("drivers", [])
    indicators = vision.get("indicators", {})
    events     = vision.get("events", [])
    top3       = vision.get("top3", [])
    lap_info   = vision.get("lap_info", {})
    lap_reel   = lap_info.get("current_lap") or lap

    # 2. ML prédiction
    race_data = {
        "lap"             : lap_reel + 1,
        "total_laps"      : total_laps,
        "current_position": drivers[0]["position"] if drivers else 1,
        "drivers"         : drivers,
        "indicators"      : indicators,
    }
    prediction = predict(race_data)

    # 3. LLM avec contexte réel
    if top3:
        predictions_list = [
            {
                "driver":      p.get("name", p.get("code", "?")),
                "team":        p.get("team", ""),
                "position":    p.get("position", i+1),
                "probability": prediction.get("probability", 50) if i == 0 else max(prediction.get("probability", 50) - (i*15), 5),
            }
            for i, p in enumerate(top3)
        ]
    else:
        predictions_list = [
            {"driver": "P1", "team": "", "position": 1, "probability": prediction.get("probability", 50)},
            {"driver": "P2", "team": "", "position": 2, "probability": 30},
            {"driver": "P3", "team": "", "position": 3, "probability": 20},
        ]

    commentary_llm = generate_commentary(
        predictions_list,
        lap=lap_reel,
        total_laps=total_laps,
        position_predite=prediction.get("position_predite", 10),
        probability=prediction.get("probability", 50),
        yolo_events=events,  #? Pour passer les events YOLO au LLM en contexte
    )

    # 4. RAG
    rag_data = {
        "event"      : events[0] if events else "race",
        "lap"        : lap_reel,
        "total_laps" : total_laps,
        "predictions": prediction,
        "drivers"    : drivers,
    }
    commentary_rag = generer_commentaire(rag_data, persona="journaliste")
    commentary_rag = commentary_rag.get("commentaire", "")

    return {
        "lap"           : lap_reel,
        "drivers"       : drivers,
        "indicators"    : indicators,
        "events"        : events,
        "prediction"    : prediction,
        "commentary_llm": commentary_llm,
        "commentary_rag": commentary_rag,
        "timestamp"     : 0,
    }


def configurer_quota(nb_frames: int):
    llm_config(nb_frames)
    rag_config(nb_frames)