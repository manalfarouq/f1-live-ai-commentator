# backend/app/services/video_service.py

import cv2
import tempfile
import os
import shutil


def sauvegarder_video(contenu: bytes, nom: str = "video.mp4") -> str:
    """Sauvegarde les bytes de la vidéo uploadée et retourne le chemin."""
    dossier = tempfile.mkdtemp()
    chemin  = os.path.join(dossier, nom)

    with open(chemin, "wb") as f:
        f.write(contenu)

    return chemin


def extraire_frames(chemin: str, intervalle: int = 2) -> list:
    """Extrait 1 frame toutes les X secondes."""
    video  = cv2.VideoCapture(chemin)
    fps    = video.get(cv2.CAP_PROP_FPS)
    frames = []
    numero = 0

    while True:
        ok, frame = video.read()
        if not ok:
            break
        if numero % int(fps * intervalle) == 0:
            frames.append({"frame": frame, "timestamp": round(numero / fps, 1)})
        numero += 1

    video.release()
    return frames