# backend/app/routes/prediction_router.py

from fastapi import APIRouter, HTTPException
from ..schemas.prediction_schema import PredictRequest, PredictResponse
from ..services.ml_service import ml_service
from ..services.llm_service import generate_commentary

router = APIRouter(tags=["Predictions"])


@router.post("/predict", response_model=PredictResponse)
def predict_winner(request: PredictRequest):
    """
    Prédire la position finale d'un pilote F1

    - **Grid**: Position de départ (1-24)
    - **Rain**: Pluie (0=sec, 1=pluie)
    - **Round**: Numéro de la course dans la saison
    - **Season**: Année
    - **DriverID**: ID du pilote
    - **ConstructorName**: Nom de l'écurie
    - **CircuitID**: ID du circuit
    - **lap** *(optionnel)*: Tour actuel (défaut: 1)
    - **total_laps** *(optionnel)*: Nombre total de tours (défaut: 58)
    - **current_position** *(optionnel)*: Position actuelle en course
    """
    try:
        data = request.model_dump()

        result = ml_service.predict(data)

        winner = result["prediction"] == 1
        probability = result["probability"]
        position = result.get("position_predite", "?")

        if winner:
            prediction_text = f"{request.DriverID} a de fortes chances de gagner à {request.CircuitID}"
        else:
            prediction_text = f"{request.DriverID} devrait terminer {position}ème à {request.CircuitID}"

        return PredictResponse(
            winner=winner,
            probability=round(probability, 2),
            prediction=prediction_text,
            driver=request.DriverID,
            circuit=request.CircuitID,
            position_predite=result.get("position_predite"),
            position_exacte=result.get("position_exacte"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}")


@router.get("/model-info")
def get_model_info():
    """Informations sur le modèle chargé"""
    from ..services.ml_service import feature_cols
    return {
        "model_type": type(ml_service.model).__name__ if ml_service.model else "Non chargé",
        "model_loaded": ml_service.model is not None,
        "model_version": "v5",
        "mae": 1.330,
        "r2": 0.859,
        "nb_features": len(feature_cols),
        "features": feature_cols,
    }

@router.post("/predict-top3")
def predict_top3(requests: list[PredictRequest]):
    """
    Prédire le Top 3 et générer un commentaire IA.
    Envoyez exactement 3 pilotes.
    """
    try:
        if len(requests) < 3:
            raise HTTPException(
                status_code=400,
                detail=f"Il faut exactement 3 pilotes. Reçu: {len(requests)}"
            )

        predictions = []
        for req in requests[:3]:  # on prend les 3 premiers
            data = req.model_dump()
            result = ml_service.predict(data)
            predictions.append({
                "driver"          : req.DriverID,
                "circuit"         : req.CircuitID,
                "constructor"     : req.ConstructorName,
                "probability"     : result["probability"],
                "position_predite": result.get("position_predite"),
                "grid"            : req.Grid,
            })

        predictions.sort(key=lambda x: x["probability"], reverse=True)

        top3 = predictions[:3]
        for i, pred in enumerate(top3, 1):
            pred["position"] = i

        commentary = generate_commentary(top3)

        return {
            "top3"      : top3,
            "commentary": commentary,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}")