import joblib
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from ..core.database import SessionLocal, EncodingMapping, init_db

# Charger le modèle
try:
    model = joblib.load('models/f1_winner_model.joblib')
    print("✅ Modèle chargé avec succès")
except Exception as e:
    print(f"❌ Erreur lors du chargement du modèle: {e}")
    model = None

# Initialiser la DB
init_db()


def get_encoding_mappings():
    """Récupérer les mappings depuis la DB"""
    db = SessionLocal()
    try:
        drivers = {m.name: m.code for m in db.query(EncodingMapping).filter_by(category='driver').all()}
        constructors = {m.name: m.code for m in db.query(EncodingMapping).filter_by(category='constructor').all()}
        circuits = {m.name: m.code for m in db.query(EncodingMapping).filter_by(category='circuit').all()}
        return drivers, constructors, circuits
    finally:
        db.close()


def prepare_features(data):
    """Prépare les features pour le modèle"""
    df = pd.DataFrame([data])
    
    # Récupérer les mappings depuis la DB
    driver_mapping, constructor_mapping, circuit_mapping = get_encoding_mappings()
    
    # Encoder les catégories
    df['DriverID_code'] = df['DriverID'].map(driver_mapping).fillna(-1).astype(int)
    df['ConstructorName_code'] = df['ConstructorName'].map(constructor_mapping).fillna(-1).astype(int)
    df['CircuitID_code'] = df['CircuitID'].map(circuit_mapping).fillna(-1).astype(int)
    
    feature_columns = [
        'Grid', 'Rain', 'Round', 'Season',
        'DriverID_code', 'ConstructorName_code', 'CircuitID_code'
    ]
    
    return df[feature_columns]


def predict(data):
    """Fait une prédiction"""
    if model is None:
        raise Exception("Le modèle n'est pas chargé")
    
    features = prepare_features(data)
    prediction = int(model.predict(features)[0])
    
    probability = 0.0
    if hasattr(model, 'predict_proba'):
        probability = float(model.predict_proba(features)[0][1]) * 100
    
    return {
        "prediction": prediction,
        "probability": probability
    }


class ml_service:
    model = model
    
    @staticmethod
    def predict(data):
        return predict(data)