# backend/app/routes/video_router.py

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Form
import uuid

from app.services.video_service import (
    sauvegarder_video,
    extraire_frames,
    analyser_frame,
    configurer_quota,
)

router = APIRouter(prefix="/video", tags=["Video"])
jobs   = {}


@router.post("/analyze")
async def analyze(
    background_tasks: BackgroundTasks,
    file      : UploadFile = File(...),
    intervalle: int        = Form(2),
):
    """Upload une vidéo et lance l'analyse en arrière-plan."""
    job_id  = str(uuid.uuid4())[:8]
    contenu = await file.read()

    jobs[job_id] = {"status": "en cours", "resultats": []}
    background_tasks.add_task(_analyser, job_id, contenu, file.filename, intervalle)
    return {"job_id": job_id, "message": f"Consulte /video/status/{job_id}"}


@router.get("/status/{job_id}")
async def status(job_id: str):
    """Retourne l'état et les résultats d'une analyse."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job introuvable")
    return jobs[job_id]


def _analyser(job_id: str, contenu: bytes, nom: str, intervalle: int):
    """Sauvegarde → extrait → configure quota → analyse chaque frame."""
    try:
        chemin = sauvegarder_video(contenu, nom)
        frames = extraire_frames(chemin, intervalle)

        # Configure Gemini automatiquement selon nb de frames
        configurer_quota(len(frames))

        resultats = []
        for i, item in enumerate(frames):
            resultat = analyser_frame(
                frame      = item["frame"],
                lap        = i + 1,
                total_laps = len(frames),
            )
            resultat["timestamp"] = item["timestamp"]
            resultats.append(resultat)

        jobs[job_id] = {"status": "terminé", "resultats": resultats}

    except Exception as e:
        jobs[job_id] = {"status": "erreur", "erreur": str(e)}