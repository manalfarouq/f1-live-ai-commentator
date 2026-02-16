import joblib
import pandas as pd
from pathlib import Path
from ..core.config import settings

class MLService:
    """Service pour les prédictions ML"""
    
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Charge le modèle ML"""
        try:
            model_path = Path(settings.MODEL_PATH)
            if not model_path.exists():
                raise FileNotFoundError(f"Modèle non trouvé: {model_path}")
            
            self.model = joblib.load(model_path)
            print(f"✅ Modèle chargé: {model_path}")
        except Exception as e:
            print(f"❌ Erreur chargement modèle: {e}")
            raise
    
    def predict(self, data: dict):
        """
        Fait une prédiction
        
        Args:
            data: dict avec les features (Grid, Rain, etc.)
        
        Returns:
            dict avec prediction et probability
        """
        if self.model is None:
            raise ValueError("Modèle non chargé")
        
        # Préparer les données
        features = self._prepare_features(data)
        
        # Prédiction
        prediction = int(self.model.predict(features)[0])
        
        # Probabilité (si le modèle le supporte)
        probability = 0.0
        if hasattr(self.model, 'predict_proba'):
            probability = float(self.model.predict_proba(features)[0][1]) * 100
        
        return {
            "prediction": prediction,
            "probability": probability
        }
    
    def _prepare_features(self, data: dict):
        """
        Prépare les features pour le modèle
        Convertit les catégories en codes
        """
        # Convertir en DataFrame
        df = pd.DataFrame([data])
        
        # Encoder les catégories (comme dans l'entraînement)
        if 'DriverID' in df.columns:
            df['DriverID_code'] = df['DriverID'].astype('category').cat.codes
        
        if 'ConstructorName' in df.columns:
            df['ConstructorName_code'] = df['ConstructorName'].astype('category').cat.codes
        
        if 'CircuitID' in df.columns:
            df['CircuitID_code'] = df['CircuitID'].astype('category').cat.codes
        
        # Sélectionner les colonnes dans le bon ordre
        feature_columns = [
            'Grid', 'Rain', 'Round', 'Season',
            'DriverID_code', 'ConstructorName_code', 'CircuitID_code'
        ]
        
        features = df[feature_columns]
        
        return features


# Instance globale du service
ml_service = MLService()
