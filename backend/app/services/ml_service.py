# backend/app/services/ml_service.py
#
# Mise à jour : on utilise maintenant f1_model_position_v5.pkl
# qui prédit la POSITION FINALE (1-20) au lieu de juste victoire oui/non
#
# Le reste du code (prediction_router.py, prediction_schema.py) ne change pas
# car on retourne toujours "prediction" et "probability"

import joblib
import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session
from ..core.database import SessionLocal, init_db

# Chemin vers les modèles
MODEL_DIR = Path(__file__).resolve().parents[2] / "models"

# Charger le nouveau modèle au démarrage
try:
    model        = joblib.load(MODEL_DIR / "f1_model_position_v5.pkl")
    feature_cols = joblib.load(MODEL_DIR / "feature_names_v5.pkl")
    print(f"✅ Modèle v5 chargé ({len(feature_cols)} features | MAE=1.33 | R²=0.86)")
except Exception as e:
    print(f"❌ Erreur lors du chargement du modèle: {e}")
    model        = None
    feature_cols = []

# Initialiser la DB (comme avant)
init_db()


def prepare_features(data: dict) -> np.ndarray:
    """
    Prépare les 43 features attendues par le modèle v5.

    Reçoit un dictionnaire avec les données de la requête.
    Retourne un vecteur numpy dans le bon ordre.
    """
    lap              = data.get("lap", 1)
    total_laps       = data.get("total_laps", 58)
    # Grid = position de départ (format ancien) ou grid_position (format nouveau)
    grid_position    = data.get("grid_position", data.get("Grid", 10))
    current_position = data.get("current_position") or grid_position
    lap_time_ms      = data.get("lap_time_ms", 90000)
    avg_lap_time_ms  = data.get("avg_lap_time_ms", 90000)
    best_lap_time_ms = data.get("best_lap_time_ms", 89000)
    lap_time_std     = data.get("lap_time_std", 500)
    nb_pit_stops     = data.get("nb_pit_stops", 0)

    race_progress_pct = round((lap / max(total_laps, 1)) * 100, 1)
    laps_remaining    = total_laps - lap

    features = {
        # Données de course
        "lap"                     : lap,
        "total_laps"              : total_laps,
        "laps_remaining"          : laps_remaining,
        "race_progress_pct"       : race_progress_pct,
        "current_position"        : current_position,
        "grid_position"           : grid_position,
        "positions_gained"        : grid_position - current_position,

        # Temps au tour
        "lap_time_ms"             : lap_time_ms,
        "avg_lap_time_ms"         : avg_lap_time_ms,
        "best_lap_time_ms"        : best_lap_time_ms,
        "lap_time_std"            : lap_time_std,
        "gap_to_leader_ms"        : data.get("gap_to_leader_ms", 0),
        "is_fastest_lap"          : data.get("is_fastest_lap", 0),

        # Pit stops
        "nb_pit_stops"            : nb_pit_stops,
        "last_pit_lap"            : data.get("last_pit_lap", 0),
        "laps_on_tyre"            : data.get("laps_on_tyre", lap),
        "last_pit_duration_ms"    : data.get("last_pit_duration_ms", 0),

        # Qualifying
        "quali_position"          : data.get("quali_position", grid_position),
        "best_quali_ms"           : data.get("best_quali_ms", 90000),
        "gap_to_quali_best"       : data.get("gap_to_quali_best", 0),

        # Championnat
        "driver_season_points"    : data.get("driver_season_points", 0),
        "driver_season_pos"       : data.get("driver_season_pos", 10),
        "driver_wins_season"      : data.get("driver_wins_season", 0),
        "constructor_points"      : data.get("constructor_points", 0),
        "constructor_pos"         : data.get("constructor_pos", 5),

        # Historique circuit
        "driver_avg_pos_circuit"  : data.get("driver_avg_pos_circuit", 10),
        "driver_wins_circuit"     : data.get("driver_wins_circuit", 0),
        "constructor_avg_circuit" : data.get("constructor_avg_circuit", 5),

        # Saison / Round (compatibilité avec l'ancien format)
        "year"                    : data.get("Season", data.get("year", 2024)),
        "round"                   : data.get("Round", data.get("round", 1)),

        # Features calculées (comme dans train_model.py)
        "lap_time_delta"       : lap_time_ms - avg_lap_time_ms,
        "pace_vs_best"         : lap_time_ms - best_lap_time_ms,
        "consistency"          : lap_time_std / (avg_lap_time_ms + 1),
        "is_early_race"        : 1 if race_progress_pct < 33 else 0,
        "is_mid_race"          : 1 if 33 <= race_progress_pct < 66 else 0,
        "is_late_race"         : 1 if race_progress_pct >= 66 else 0,
        "position_momentum"    : grid_position - current_position,
        "has_pitted"           : 1 if nb_pit_stops > 0 else 0,
        "pit_frequency"        : nb_pit_stops / (lap + 1),
        "late_top5"            : 1 if current_position <= 5 and race_progress_pct >= 66 else 0,
        "recovery_potential"   : laps_remaining / (current_position + 1),
        "pace_gap_to_leader"   : data.get("pace_gap_to_leader", 0),
        "overtake_opportunity" : grid_position - current_position,
    }

    # Retourner le vecteur dans le bon ordre (ordre du modèle)
    return np.array([features.get(col, 0) for col in feature_cols]).reshape(1, -1)


def predict(data: dict) -> dict:
    """
    Prédit la position finale d'un pilote (1 à 20).

    Retourne un dict compatible avec l'ancien format :
    - "prediction"  : 1 si le pilote gagne (position=1), 0 sinon
    - "probability" : probabilité de victoire (0-100%)

    + nouvelles infos :
    - "position_predite" : position finale prédite (1-20)
    """
    if model is None:
        raise Exception("Le modèle n'est pas chargé")

    X = prepare_features(data)

    # Prédire et clipper entre 1 et 20
    position_predite  = float(np.clip(model.predict(X)[0], 1, 20))
    position_arrondie = round(position_predite)

    # Probabilité de victoire : position 1 = ~100%, position 20 = ~0%
    probability = round((20 - position_predite) / 19 * 100, 1)

    return {
        # ← Format compatible avec prediction_router.py existant
        "prediction"      : 1 if position_arrondie == 1 else 0,
        "probability"     : probability,

        # ← Nouvelles infos
        "position_predite": position_arrondie,
        "position_exacte" : round(position_predite, 2),
    }


# Classe pour compatibilité avec prediction_router.py
class ml_service:
    model = model

    @staticmethod
    def predict(data: dict) -> dict:
        return predict(data)