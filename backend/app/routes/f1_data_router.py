# backend/app/routes/f1_data_router.py

from fastapi import APIRouter, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.f1_db_service import save_race_data, get_all_races, get_race_by_id, get_driver_history
import shutil
import os

router = APIRouter(prefix="/f1-data", tags=["F1 Data"])


@router.get("/test")
async def test_endpoint():
    return {"status": "F1 Data Router OK 🏎️"}


@router.post("/debug")
async def debug_ocr(file: UploadFile = File(...)):
    """Debug : voir tout ce que l'OCR détecte"""
    import sys

    notebooks_path = '/app/notebooks'
    if notebooks_path not in sys.path:
        sys.path.insert(0, notebooks_path)

    try:
        from reconnaissance_dobjets import extract_text_from_image
    except Exception as e:
        return {"error": f"Import failed: {str(e)}"}

    os.makedirs("data/images", exist_ok=True)
    temp_path = f"data/images/temp_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ocr_results = extract_text_from_image(temp_path)

        debug_data = []
        for (bbox, text, prob) in ocr_results:
            debug_data.append({
                "text": text,
                "confidence": round(prob, 2),
                "y_position": int(bbox[0][1])
            })

        debug_data.sort(key=lambda x: x['y_position'])

        return {
            "total_detected": len(debug_data),
            "all_text": debug_data
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/extract")
async def extract_f1_data(
    file: UploadFile = File(...),
    save_to_db: bool = Query(False, description="Sauvegarder dans la base de données"),
    race_name: str = Query(None, description="Nom de la course (optionnel)"),
    circuit: str = Query(None, description="Nom du circuit (optionnel)"),
    db: Session = Depends(get_db)
):
    """
    Upload une image et extrait les données F1 complètes
    Peut sauvegarder dans la DB si save_to_db=true
    """
    import sys

    notebooks_path = '/app/notebooks'
    if notebooks_path not in sys.path:
        sys.path.insert(0, notebooks_path)

    try:
        from reconnaissance_dobjets import get_f1_data, save_data_to_dict
    except Exception as e:
        return {"error": f"Import failed: {str(e)}"}

    os.makedirs("data/images", exist_ok=True)
    temp_path = f"data/images/temp_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        f1_data = get_f1_data(temp_path)
        result = save_data_to_dict(f1_data)

        if save_to_db:
            race = save_race_data(db, f1_data, race_name, circuit)
            result["saved_to_db"] = True
            result["race_id"] = race.id

        return result

    except Exception as e:
        return {"error": str(e)}

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/races")
async def get_races(limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    """Récupère l'historique des courses"""
    races = get_all_races(db, limit=limit)
    return {
        "total": len(races),
        "races": [
            {
                "id": race.id,
                "race_name": race.race_name,
                "circuit": race.circuit,
                "current_lap": race.current_lap,
                "total_laps": race.total_laps,
                "progress_percentage": race.progress_percentage,
                "timestamp": race.timestamp.isoformat()
            }
            for race in races
        ]
    }


@router.get("/races/{race_id}")
async def get_race_details(race_id: int, db: Session = Depends(get_db)):
    """Récupère les détails d'une course spécifique"""
    race = get_race_by_id(db, race_id)

    if not race:
        return {"error": "Race not found"}

    return {
        "id": race.id,
        "race_name": race.race_name,
        "circuit": race.circuit,
        "current_lap": race.current_lap,
        "total_laps": race.total_laps,
        "progress_percentage": race.progress_percentage,
        "timestamp": race.timestamp.isoformat(),
        "positions": [
            {
                "position": pos.position,
                "driver": pos.driver,
                "team": pos.team,
                "interval": pos.interval
            }
            for pos in sorted(race.positions, key=lambda x: x.position)
        ]
    }


@router.get("/drivers/{driver_code}/history")
async def get_driver_stats(driver_code: str, limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """Récupère l'historique des positions d'un pilote"""
    history = get_driver_history(db, driver_code.upper(), limit=limit)

    return {
        "driver": driver_code.upper(),
        "total_entries": len(history),
        "history": [
            {
                "race_id": pos.race_id,
                "position": pos.position,
                "team": pos.team,
                "interval": pos.interval,
                "timestamp": pos.timestamp.isoformat()
            }
            for pos in history
        ]
    }


@router.post("/analyser-et-predire")
async def analyser_et_predire(
    file: UploadFile = File(...),
    circuit: str = Query("unknown", description="Nom du circuit"),
    rain: int = Query(0, description="Pluie (0=sec, 1=pluie)"),
    round_num: int = Query(1, description="Numéro de la manche"),
    season: int = Query(2026, description="Saison"),
    db: Session = Depends(get_db)
):
    """
    Pipeline complet : Image → OCR → Prédictions ML → Commentaire IA

    1. Extrait les données de l'image (pilotes, tour, positions)
    2. Prédit la position finale de chaque pilote actif
    3. Génère un commentaire IA sur le Top 3
    """
    import sys
    sys.path.insert(0, '/app/notebooks')

    try:
        from reconnaissance_dobjets import get_f1_data, save_data_to_dict
    except Exception as e:
        return {"error": f"Import failed: {str(e)}"}

    from app.services.ml_service import predict
    from app.services.llm_service import generate_commentary

    os.makedirs("data/images", exist_ok=True)
    temp_path = f"data/images/temp_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. Extraction OCR
        f1_data = get_f1_data(temp_path)
        extracted = save_data_to_dict(f1_data)

        drivers     = extracted.get("drivers", [])
        lap_info    = extracted.get("lap_info", {})
        current_lap = lap_info.get("current_lap", 1)
        total_laps  = lap_info.get("total_laps", 58)

        if not drivers:
            return {"error": "Aucun pilote détecté dans l'image"}

        # 2. Prédiction ML pour chaque pilote actif
        predictions = []
        skipped     = []

        for driver in drivers:
            # Ignorer pilotes sans code ou abandonnés (Out, IN PIT...)
            if not driver.get("driver"):
                continue

            interval = driver.get("interval", "")
            if isinstance(interval, str) and interval.strip().lower() in ("out", "in pit", "dnf", "dns"):
                skipped.append({
                    "position": driver["position"],
                    "driver"  : driver["driver"],
                    "status"  : interval.strip()
                })
                continue

            data = {
                "Grid"            : driver["position"],
                "Rain"            : rain,
                "Round"           : round_num,
                "Season"          : season,
                "DriverID"        : driver["driver"].lower(),
                "ConstructorName" : driver.get("team", "Unknown"),
                "CircuitID"       : circuit,
                "lap"             : current_lap,
                "total_laps"      : total_laps,
                "current_position": driver["position"],
            }

            result = predict(data)

            predictions.append({
                "position_actuelle": driver["position"],
                "driver"           : driver["driver"],
                "team"             : driver.get("team", "Unknown"),
                "interval"         : interval,
                "probability"      : result["probability"],
                "position_predite" : result["position_predite"],
            })

        if not predictions:
            return {"error": "Aucun pilote actif pour la prédiction"}

        # Trier par probabilité décroissante
        predictions.sort(key=lambda x: x["probability"], reverse=True)

        # Top 3
        top3 = predictions[:3]
        for i, pred in enumerate(top3, 1):
            pred["position_podium"] = i

        # 3. Commentaire IA
        commentary = generate_commentary(top3)

        return {
            "lap_info"       : lap_info,
            "total_drivers"  : len(drivers),
            "active_drivers" : len(predictions),
            "skipped"        : skipped,
            "top3"           : top3,
            "commentary"     : commentary,
            "all_predictions": predictions,
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)