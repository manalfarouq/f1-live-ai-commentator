from fastapi import APIRouter, HTTPException
from ..schemas.prediction_schema import PredictRequest, PredictResponse
from ..services.ml_service import ml_service

router = APIRouter(tags=["Predictions"])

@router.post("/predict", response_model=PredictResponse)
def predict_winner(request: PredictRequest):
    """
    Prédire qui va gagner la course F1
    
    - **Grid**: Position de départ (1-24)
    - **Rain**: Pluie (0=sec, 1=pluie)
    - **Round**: Numéro de la course dans la saison
    - **Season**: Année
    - **DriverID**: ID du pilote
    - **ConstructorName**: Nom de l'écurie
    - **CircuitID**: ID du circuit
    """
    try:
        # Convertir la requête en dict
        data = request.model_dump()
        
        # Faire la prédiction
        result = ml_service.predict(data)
        
        # Préparer la réponse
        winner = result["prediction"] == 1
        probability = result["probability"]
        
        # Générer le message
        if winner:
            prediction_text = f"{request.DriverID} a de fortes chances de gagner à {request.CircuitID}"
        else:
            prediction_text = f"{request.DriverID} ne devrait pas gagner à {request.CircuitID}"
        
        return PredictResponse(
            winner=winner,
            probability=round(probability, 2),
            prediction=prediction_text,
            driver=request.DriverID,
            circuit=request.CircuitID
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction: {str(e)}"
        )


@router.get("/model-info")
def get_model_info():
    """Informations sur le modèle"""
    return {
        "model_type": type(ml_service.model).__name__ if ml_service.model else "Non chargé",
        "model_loaded": ml_service.model is not None,
        "features": [
            "Grid", "Rain", "Round", "Season",
            "DriverID_code", "ConstructorName_code", "CircuitID_code"
        ]
    }
