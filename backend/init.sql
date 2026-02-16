-- La base de données f1_predictions est déjà créée par POSTGRES_DB
-- Pas besoin de CREATE DATABASE

-- Créer la table pour les mappings d'encodage
CREATE TABLE IF NOT EXISTS encoding_mappings (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    code INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category, name)
);

-- Créer des index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_category ON encoding_mappings(category);
CREATE INDEX IF NOT EXISTS idx_name ON encoding_mappings(name);

-- Créer une table pour stocker les prédictions historiques (optionnel)
CREATE TABLE IF NOT EXISTS predictions_history (
    id SERIAL PRIMARY KEY,
    driver_id VARCHAR(100) NOT NULL,
    constructor_name VARCHAR(100) NOT NULL,
    circuit_id VARCHAR(100) NOT NULL,
    grid_position INTEGER NOT NULL,
    rain INTEGER NOT NULL,
    round INTEGER NOT NULL,
    season INTEGER NOT NULL,
    prediction INTEGER NOT NULL,
    probability FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_driver ON predictions_history(driver_id);
CREATE INDEX IF NOT EXISTS idx_circuit ON predictions_history(circuit_id);
CREATE INDEX IF NOT EXISTS idx_season ON predictions_history(season);

-- Insérer des données d'exemple pour les encodages
-- IMPORTANT: Ces données sont des exemples, vous devrez les remplacer par vos vraies données

-- Exemple de pilotes
INSERT INTO encoding_mappings (category, name, code) VALUES 
    ('driver', 'hamilton', 0),
    ('driver', 'verstappen', 1),
    ('driver', 'leclerc', 2),
    ('driver', 'sainz', 3),
    ('driver', 'perez', 4),
    ('driver', 'norris', 5),
    ('driver', 'russell', 6),
    ('driver', 'alonso', 7),
    ('driver', 'ocon', 8),
    ('driver', 'gasly', 9),
    ('driver', 'max', 10)
ON CONFLICT (category, name) DO NOTHING;

-- Exemple d'écuries
INSERT INTO encoding_mappings (category, name, code) VALUES 
    ('constructor', 'Mercedes', 0),
    ('constructor', 'Red Bull', 1),
    ('constructor', 'Ferrari', 2),
    ('constructor', 'McLaren', 3),
    ('constructor', 'Alpine', 4),
    ('constructor', 'Aston Martin', 5),
    ('constructor', 'Williams', 6),
    ('constructor', 'Alfa Romeo', 7),
    ('constructor', 'Haas', 8),
    ('constructor', 'AlphaTauri', 9)
ON CONFLICT (category, name) DO NOTHING;

-- Exemple de circuits
INSERT INTO encoding_mappings (category, name, code) VALUES 
    ('circuit', 'monaco', 0),
    ('circuit', 'silverstone', 1),
    ('circuit', 'monza', 2),
    ('circuit', 'spa', 3),
    ('circuit', 'suzuka', 4),
    ('circuit', 'interlagos', 5),
    ('circuit', 'bahrain', 6),
    ('circuit', 'melbourne', 7),
    ('circuit', 'barcelona', 8),
    ('circuit', 'austin', 9)
ON CONFLICT (category, name) DO NOTHING;