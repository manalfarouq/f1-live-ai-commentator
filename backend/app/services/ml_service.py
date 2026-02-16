# - Service ML - Prédiction F1
# - Chargement et test du modèle

import joblib
import pandas as pd
import numpy as np


# - Charger le modèle

# Charger le modèle entraîné
try:
    model = joblib.load('models/f1_winner_model.joblib')
    print("✅ Modèle chargé avec succès")
except Exception as e:
    print(f"❌ Erreur lors du chargement du modèle: {e}")
    model = None


# - Fonctions de prédiction

def prepare_features(data):
    """
    Prépare les features pour le modèle
    Convertit les catégories en codes
    """
    # Convertir en DataFrame
    df = pd.DataFrame([data])

    # Encoder les catégories
    df['DriverID_code'] = df['DriverID'].astype('category').cat.codes
    df['ConstructorName_code'] = df['ConstructorName'].astype('category').cat.codes
    df['CircuitID_code'] = df['CircuitID'].astype('category').cat.codes

    # Sélectionner les colonnes dans le bon ordre
    feature_columns = [
        'Grid', 'Rain', 'Round', 'Season',
        'DriverID_code', 'ConstructorName_code', 'CircuitID_code'
    ]

    features = df[feature_columns]

    return features


def predict(data):
    """
    Fait une prédiction
    Retourne la prédiction et la probabilité
    """
    if model is None:
        raise Exception("Le modèle n'est pas chargé")
    
    # Préparer les features
    features = prepare_features(data)

    # Prédiction
    prediction = int(model.predict(features)[0])

    # Probabilité
    probability = 0.0
    if hasattr(model, 'predict_proba'):
        probability = float(model.predict_proba(features)[0][1]) * 100

    return {
        "prediction": prediction,
        "probability": probability
    }


# Créer un objet simple pour l'import compatible avec votre router
class ml_service:
    model = model
    
    @staticmethod
    def predict(data):
        return predict(data)