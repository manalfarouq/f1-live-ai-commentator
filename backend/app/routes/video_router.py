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
    job_id  = str(uuid.uuid4())[:8]
    contenu = await file.read()
    jobs[job_id] = {"status": "en cours", "resultats": []}
    background_tasks.add_task(_analyser, job_id, contenu, file.filename, intervalle)
    return {"job_id": job_id, "message": f"Consulte /video/status/{job_id}"}


@router.get("/status/{job_id}")
async def status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job introuvable")
    return jobs[job_id]


def _analyser(job_id: str, contenu: bytes, nom: str, intervalle: int):
    try:
        chemin = sauvegarder_video(contenu, nom)
        frames = extraire_frames(chemin, intervalle)
        configurer_quota(len(frames))

        duree_totale   = len(frames) * intervalle
        total_laps_est = max(1, duree_totale // 90)

        resultats = []
        lap_index = {}

        for i, item in enumerate(frames):
            # Estimer le tour via timestamp (1 tour F1 ~ 90s)
            lap_estime = max(1, item["timestamp"] // 90 + 1)

            resultat = analyser_frame(
                frame      = item["frame"],
                lap        = lap_estime,
                total_laps = total_laps_est,
            )
            resultat["timestamp"] = item["timestamp"]

            lap_num = resultat.get("lap", lap_estime)

            if lap_num in lap_index:
                resultats[lap_index[lap_num]] = resultat
            else:
                lap_index[lap_num] = len(resultats)
                resultats.append(resultat)

            jobs[job_id]["resultats"] = sorted(resultats, key=lambda r: r.get("lap", 0))

        jobs[job_id] = {
            "status"   : "terminé",
            "resultats": sorted(resultats, key=lambda r: r.get("lap", 0)),
        }

    except Exception as e:
        jobs[job_id] = {"status": "erreur", "erreur": str(e), "message": str(e)}