from fastapi import APIRouter, HTTPException
from ..schemas.prediction_schema import PredictRequest, PredictResponse
from ..services.ml_service import ml_service

from ..services.llm_service import generate_commentary

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

@router.post("/predict-top3")
def predict_top3(requests: list[PredictRequest]):
    """
    Prédire le Top 3 et générer un commentaire IA
    
    Envoyez une liste de 3+ pilotes avec leurs informations
    """
    try:
        if len(requests) < 3:
            raise HTTPException(
                status_code=400,
                detail="Il faut au moins 3 pilotes pour prédire le Top 3"
            )
        
        # Faire les prédictions pour tous les pilotes
        predictions = []
        for req in requests:
            data = req.model_dump()
            result = ml_service.predict(data)
            
            predictions.append({
                'driver': req.DriverID,
                'circuit': req.CircuitID,
                'constructor': req.ConstructorName,
                'probability': result['probability'],
                'grid': req.Grid
            })
        
        # Trier par probabilité décroissante
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        
        # Top 3
        top3 = predictions[:3]
        
        # Ajouter les positions
        for i, pred in enumerate(top3, 1):
            pred['position'] = i
        
        # Générer le commentaire IA
        commentary = generate_commentary(top3)
        
        return {
            "top3": top3,
            "commentary": commentary
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction: {str(e)}"
        )
