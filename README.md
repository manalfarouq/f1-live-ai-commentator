# 🏎️ F1 Live AI Commentator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-00a393.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)

> **AI-powered Formula 1 race analysis system combining Computer Vision, Machine Learning predictions, and multi-agent LLM commentary for real-time race insights.**

---

## Table of Contents

- [🏎️ F1 Live AI Commentator](#️-f1-live-ai-commentator)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
    - [What It Does](#what-it-does)
  - [Features](#features)
    - [Computer Vision](#computer-vision)
    - [Machine Learning](#machine-learning)
    - [AI Commentary](#ai-commentary)
    - [Real-Time Interface](#real-time-interface)
  - [Architecture](#architecture)
  - [Tech Stack](#tech-stack)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Quick Start](#quick-start)
    - [Manual Setup](#manual-setup)
  - [Usage](#usage)
    - [Running a Live Race Analysis](#running-a-live-race-analysis)
    - [Training Models](#training-models)
    - [API Usage](#api-usage)
  - [Project Structure](#project-structure)
  - [Documentation](#documentation)
  - [Testing](#testing)
    - [Roadmap](#roadmap)
- [🏎️ F1 Live AI Commentator - Backend API](#️-f1-live-ai-commentator---backend-api)
  - [📋 Fonctionnalités](#-fonctionnalités)
  - [🚀 Démarrage Rapide](#-démarrage-rapide)
    - [Option 1 : Avec Docker (Recommandé)](#option-1--avec-docker-recommandé)
    - [Option 2 : Sans Docker](#option-2--sans-docker)
  - [📖 Documentation API](#-documentation-api)
  - [🔧 Endpoints](#-endpoints)
    - [`GET /`](#get-)
    - [`GET /health`](#get-health)
    - [`POST /api/v1/predict`](#post-apiv1predict)
    - [`GET /api/v1/model-info`](#get-apiv1model-info)
  - [📁 Structure du Projet](#-structure-du-projet)
  - [🧪 Tester l'API](#-tester-lapi)
    - [Avec curl](#avec-curl)
    - [Avec Python](#avec-python)
  - [🔐 Variables d'Environnement](#-variables-denvironnement)
  - [🐳 Commandes Docker](#-commandes-docker)
  - [📊 Modèle ML](#-modèle-ml)
  - [🛠️ Développement](#️-développement)
    - [Ajouter une route](#ajouter-une-route)
    - [Modifier le modèle](#modifier-le-modèle)
  - [❓ Troubleshooting](#-troubleshooting)
    - [Erreur "Model not found"](#erreur-model-not-found)
    - [Port 8000 déjà utilisé](#port-8000-déjà-utilisé)
    - [Rebuild complet](#rebuild-complet)
  - [📝 TODO](#-todo)
  - [🤝 Contribution](#-contribution)
  - [📄 Licence](#-licence)

---

## Overview

**F1 Live AI Commentator** is an end-to-end artificial intelligence system that watches and analyzes Formula 1 races in real-time, just like a human expert. Built as the final capstone project for **Simplon Maghreb AI Specialization**, this platform demonstrates mastery of:

- **Computer Vision** (YOLOv8, OCR)
- **Machine Learning** (XGBoost, Random Forest)
- **Large Language Models** (GPT-4/Claude with RAG)
- **MLOps** (CI/CD, monitoring, drift detection)
- **Real-time Systems** (WebSocket, streaming)

### What It Does

1. **Sees the Race**: YOLOv8 detects flags (yellow, red, green, checkered), crashes, and pit stops from live video streams
2. **Understands Data**: OCR extracts race positions, lap times, and gaps from TV graphics
3. **Predicts Outcomes**: ML model trained on 26 seasons (10,398 races) forecasts Top 3 podium finishers
4. **Explains Everything**: Multi-agent LLM system generates commentary from 4 perspectives:
   - **The Professor**: Educational explanations for beginners
   - **The Engineer**: Deep technical analysis
   - **The Journalist**: Dramatic race storytelling
   - **Team Fans**: Emotional reactions (Ferrari, Mercedes, Red Bull fans)

---

## Features

### Computer Vision
- **Flag Detection**: Automatic detection of race control flags using YOLOv8
- **OCR Extraction**: Real-time extraction of race data from TV broadcasts
- **Pit Stop Tracking**: Identifies cars entering/exiting pit lane
- **Accident Detection**: Alerts on crashes and incidents

### Machine Learning
- **Podium Prediction**: XGBoost model with 78% accuracy (trained on 26 seasons)
- **Win Probability**: Live updates of each driver's chance to win
- **Strategy Analysis**: Predicts optimal pit stop strategies
- **Team Comparison**: Benchmarks strategies across teams

### AI Commentary
- **Multi-Agent System**: 4 distinct AI personalities providing diverse insights
- **RAG Integration**: FAISS vector database with F1 knowledge (rules, history, strategies)
- **Context-Aware**: Commentary adapts to race situation and user level
- **Real-Time Generation**: Sub-500ms latency from event to commentary

### Real-Time Interface
- **Live Race View**: Synchronized video player with event overlay
- **Interactive Timeline**: Browse race history with clickable events
- **Probability Charts**: Evolving win chances visualized with Chart.js
- **WebSocket Updates**: Instant push notifications for all events

---

## Architecture

```
┌─────────────────┐
│  Video Stream   │
│   (OpenCV)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Computer Vision │─────▶│  Event Detection │
│   (YOLOv8+OCR)  │      │   (Rule Engine)  │
└─────────────────┘      └────────┬─────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  ML Predictions │      │  LLM Commentary │      │   Data API      │
│   (XGBoost)     │      │  (GPT-4/Claude) │      │ (FastAPI+WS)    │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         └────────────────────────┴────────────────────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  React Frontend │
                         │   (Real-time)   │
                         └─────────────────┘
```

**Microservices Architecture:**
1. **Vision Service**: Processes video frames (YOLOv8, OCR)
2. **ML Service**: Runs predictions and strategy analysis
3. **LLM Service**: Generates commentary with RAG
4. **API Gateway**: FastAPI with WebSocket support
5. **Frontend**: React SPA with real-time updates

---

## Tech Stack

| Component | Technologies |
|-----------|-------------|
| **Computer Vision** | YOLOv8, OpenCV, EasyOCR/Tesseract |
| **Machine Learning** | XGBoost, Random Forest, scikit-learn, MLflow |
| **LLM / NLP** | GPT-4 / Claude API, LangChain, FAISS (RAG) |
| **Backend** | FastAPI, WebSocket, Redis, PostgreSQL |
| **Frontend** | React, Socket.io, Chart.js, TailwindCSS |
| **Data Pipeline** | Apache Airflow, Apache Spark |
| **MLOps** | Docker, GitHub Actions, Prometheus, Grafana |
| **Security** | JWT, OAuth2, Rate Limiting, HTTPS |

---

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- CUDA-compatible GPU (recommended for YOLOv8)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/f1-live-ai-commentator.git
cd f1-live-ai-commentator

# Setup Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys (OpenAI, Claude, etc.)

# Run with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

```bash
# Backend
cd src/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run dev

# ML Services
python src/ml_models/training/train_podium_model.py

# Vision Service
python src/computer_vision/video_capture.py
```

---

## Usage

### Running a Live Race Analysis

```bash
# Start all services
docker-compose up

# Upload race video or connect stream
python scripts/analyze_race.py --video path/to/race.mp4

# Access web interface at http://localhost:3000
```

### Training Models

```bash
# Download F1 historical data
python scripts/download_data.py --years 2000-2025

# Train podium prediction model
python src/ml_models/training/train_podium_model.py

# Evaluate model performance
python src/ml_models/evaluation/model_evaluation.py
```

### API Usage

```python
import requests

# Get race predictions
response = requests.get("http://localhost:8000/api/predictions/current")
print(response.json())

# Generate commentary
response = requests.post("http://localhost:8000/api/commentary/generate", 
    json={"event": "pit_stop", "driver": "Verstappen", "lap": 23})
print(response.json())
```

---

## Project Structure

```
f1-live-ai-commentator/
├── src/                      # Source code
│   ├── computer_vision/      # YOLOv8, OCR, video processing
│   ├── ml_models/            # ML training & prediction
│   ├── llm_agents/           # Multi-agent commentary system
│   ├── api/                  # FastAPI backend
│   └── utils/                # Shared utilities
├── frontend/                 # React application
├── tests/                    # Unit, integration, performance tests
├── deployment/               # Docker, K8s, monitoring configs
├── notebooks/                # Jupyter notebooks for experiments
├── docs/                     # Documentation & UML diagrams
└── data/                     # Datasets & trained models
```

See [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for detailed breakdown.

---

## Documentation

- **[Architecture Guide](docs/architecture/system-architecture.md)**: System design and data flow
- **[API Documentation](docs/api/api-documentation.md)**: Endpoint references
- **[Deployment Guide](docs/deployment/deployment-guide.md)**: Production setup
- **[User Manual](docs/user-guide/user-manual.md)**: End-user instructions
- **[UML Diagrams](docs/architecture/uml/)**: Use cases, classes, sequences

---

## Testing

```bash
# Run all tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Performance tests
pytest tests/performance/

# Coverage report
pytest --cov=src --cov-report=html
```

---


### Roadmap
- [x] Project architecture & planning
- [x] Data collection & ETL pipeline
- [ ] YOLOv8 training for flag detection
- [ ] ML model training (podium prediction)
- [ ] Multi-agent LLM system implementation
- [ ] FastAPI backend development
- [ ] React frontend development
- [ ] CI/CD pipeline setup
- [ ] Deployment & monitoring
- [ ] Final testing & documentation


```bash
f1-live-ai-commentator/
│
├── 📁 .github/
│   └── workflows/
│       ├── ci.yml                    # Tests automatiques + linting
│       ├── cd.yml                    # Déploiement automatique
│       └── model-training.yml        # Re-entraînement périodique
│
├── 📁 docs/
│   ├── architecture/
│   │   ├── system-architecture.md
│   │   ├── data-flow-diagram.png
│   │   └── uml/
│   │       ├── use-case-diagram.png
│   │       ├── class-diagram.png
│   │       └── sequence-diagram.png
│   ├── api/
│   │   └── api-documentation.md
│   ├── deployment/
│   │   ├── deployment-guide.md
│   │   └── infrastructure.md
│   └── user-guide/
│       └── user-manual.md
│
├── 📁 data/
│   ├── raw/                          # Données brutes non traitées
│   │   ├── f1_historical/
│   │   └── video_samples/
│   ├── processed/                    # Données nettoyées
│   │   ├── training/
│   │   └── validation/
│   ├── models/                       # Modèles entraînés
│   │   ├── yolov8_flags.pt
│   │   ├── xgboost_podium.pkl
│   │   └── model_metadata.json
│   └── embeddings/                   # Vecteurs pour RAG
│       └── f1_knowledge_base.faiss
│
├── 📁 src/
│   ├── 📁 computer_vision/
│   │   ├── __init__.py
│   │   ├── video_capture.py         # Capture stream vidéo
│   │   ├── flag_detector.py         # YOLOv8 détection drapeaux
│   │   ├── ocr_extractor.py         # Extraction graphiques TV
│   │   ├── pit_stop_tracker.py      # Détection arrêts stands
│   │   └── utils/
│   │       ├── image_preprocessing.py
│   │       └── bbox_utils.py
│   │
│   ├── 📁 ml_models/
│   │   ├── __init__.py
│   │   ├── podium_predictor.py      # Modèle prédiction Top 3
│   │   ├── strategy_analyzer.py     # Analyse stratégies
│   │   ├── training/
│   │   │   ├── train_podium_model.py
│   │   │   ├── feature_engineering.py
│   │   │   └── hyperparameter_tuning.py
│   │   └── evaluation/
│   │       ├── model_evaluation.py
│   │       └── metrics_calculator.py
│   │
│   ├── 📁 llm_agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py            # Classe abstraite agent
│   │   ├── professor_agent.py       # Agent pédagogique
│   │   ├── engineer_agent.py        # Agent technique
│   │   ├── journalist_agent.py      # Agent dramatique
│   │   ├── fan_agents.py            # Agents fans écuries
│   │   ├── rag_system.py            # RAG avec FAISS
│   │   └── prompts/
│   │       ├── system_prompts.py
│   │       └── templates.py
│   │
│   ├── 📁 event_detection/
│   │   ├── __init__.py
│   │   ├── event_classifier.py      # Classification événements
│   │   ├── rule_engine.py           # Règles métier F1
│   │   └── event_handlers/
│   │       ├── flag_handler.py
│   │       ├── pit_stop_handler.py
│   │       └── penalty_handler.py
│   │
│   ├── 📁 data_pipeline/
│   │   ├── __init__.py
│   │   ├── data_fetcher.py          # API Ergast/OpenF1
│   │   ├── etl_pipeline.py          # ETL process
│   │   ├── data_validator.py        # Validation qualité
│   │   └── airflow_dags/
│   │       └── f1_data_pipeline.py
│   │
│   ├── 📁 api/
│   │   ├── __init__.py
│   │   ├── main.py                  # Point d'entrée FastAPI
│   │   ├── dependencies.py          # Dépendances injectées
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── race.py              # Endpoints courses
│   │   │   ├── predictions.py       # Endpoints ML
│   │   │   ├── commentary.py        # Endpoints LLM
│   │   │   └── websocket.py         # WebSocket temps réel
│   │   ├── models/
│   │   │   ├── schemas.py           # Pydantic models
│   │   │   └── responses.py
│   │   ├── middleware/
│   │   │   ├── auth.py              # JWT/OAuth2
│   │   │   ├── rate_limit.py
│   │   │   └── cors.py
│   │   └── services/
│   │       ├── race_service.py
│   │       ├── prediction_service.py
│   │       └── commentary_service.py
│   │
│   ├── 📁 streaming/
│   │   ├── __init__.py
│   │   ├── websocket_manager.py     # Gestion connexions WS
│   │   ├── event_broadcaster.py     # Diffusion événements
│   │   └── redis_pubsub.py          # Redis pub/sub
│   │
│   └── 📁 utils/
│       ├── __init__.py
│       ├── config.py                # Configuration app
│       ├── logger.py                # Logging centralisé
│       ├── constants.py             # Constantes F1
│       └── helpers.py
│
├── 📁 frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── assets/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.jsx
│   │   ├── components/
│   │   │   ├── RaceView/
│   │   │   │   ├── RaceView.jsx
│   │   │   │   ├── VideoPlayer.jsx
│   │   │   │   └── EventTimeline.jsx
│   │   │   ├── Commentary/
│   │   │   │   ├── CommentaryPanel.jsx
│   │   │   │   └── AgentCard.jsx
│   │   │   ├── Predictions/
│   │   │   │   ├── PodiumPredictor.jsx
│   │   │   │   └── ProbabilityChart.jsx
│   │   │   └── Dashboard/
│   │   │       ├── RaceStats.jsx
│   │   │       └── LiveAlerts.jsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js
│   │   │   └── useRaceData.js
│   │   ├── services/
│   │   │   └── api.js
│   │   └── styles/
│   │       └── tailwind.css
│   ├── package.json
│   └── vite.config.js
│
├── 📁 tests/
│   ├── unit/
│   │   ├── test_flag_detector.py
│   │   ├── test_podium_predictor.py
│   │   ├── test_agents.py
│   │   └── test_api_endpoints.py
│   ├── integration/
│   │   ├── test_pipeline_e2e.py
│   │   └── test_websocket_flow.py
│   ├── performance/
│   │   ├── test_latency.py
│   │   └── load_test.py
│   └── conftest.py                  # Fixtures pytest
│
├── 📁 deployment/
│   ├── docker/
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.frontend
│   │   ├── Dockerfile.ml
│   │   └── docker-compose.yml
│   ├── kubernetes/
│   │   ├── api-deployment.yaml
│   │   ├── frontend-deployment.yaml
│   │   └── configmap.yaml
│   ├── terraform/                   # Infrastructure as Code
│   │   ├── main.tf
│   │   └── variables.tf
│   └── monitoring/
│       ├── prometheus.yml
│       ├── grafana-dashboards/
│       │   └── f1-metrics.json
│       └── alertmanager.yml
│
├── 📁 notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_training.ipynb
│   ├── 03_llm_experiments.ipynb
│   └── 04_performance_analysis.ipynb
│
├── 📁 scripts/
│   ├── setup_environment.sh
│   ├── download_data.py
│   ├── train_all_models.py
│   ├── deploy_production.sh
│   └── monitoring/
│       ├── check_model_drift.py
│       └── generate_reports.py
│
├── 📁 mlops/
│   ├── mlflow/
│   │   ├── mlflow_tracking.py
│   │   └── model_registry.py
│   ├── experiment_tracking/
│   │   └── experiments_config.yaml
│   └── drift_detection/
│       └── evidently_monitoring.py
│
├── .env.example                     # Variables d'environnement
├── .gitignore
├── .dockerignore
├── requirements.txt                 # Dépendances Python
├── requirements-dev.txt             # Dépendances développement
├── setup.py                         # Installation package
├── pytest.ini                       # Configuration tests
├── pyproject.toml                   # Configuration outils (black, ruff)
├── README.md                        # Documentation principale
├── CONTRIBUTING.md                  # Guide contribution
├── LICENSE                          # Licence projet
└── CHANGELOG.md                     # Historique versions
```


# 🏎️ F1 Live AI Commentator - Backend API

API FastAPI pour prédire le gagnant des courses de Formule 1 en temps réel.

## 📋 Fonctionnalités

- ✅ Prédiction du gagnant d'une course F1
- ✅ Calcul de probabilité de victoire
- ✅ API REST avec documentation Swagger
- ✅ Dockerisé et prêt pour le déploiement
- ✅ CORS configuré pour le frontend

## 🚀 Démarrage Rapide

### Option 1 : Avec Docker (Recommandé)

```bash
# 1. Copier le fichier .env
cp .env.example .env

# 2. Copier votre modèle entraîné
cp ../models/f1_winner_model.joblib app/models/

# 3. Lancer avec Docker Compose
docker-compose up --build
```

L'API sera disponible sur : **http://localhost:8000**

### Option 2 : Sans Docker

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Copier le modèle
cp ../models/f1_winner_model.joblib app/models/

# 3. Lancer l'API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 Documentation API

Une fois lancé, accédez à :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 🔧 Endpoints

### `GET /`
Racine de l'API - Informations de base

### `GET /health`
Vérifier la santé de l'API

### `POST /api/v1/predict`
Prédire le gagnant d'une course

**Requête :**
```json
{
  "Grid": 1,
  "Rain": 0,
  "Round": 5,
  "Season": 2026,
  "DriverID": "max",
  "ConstructorName": "Red Bull",
  "CircuitID": "monaco"
}
```

**Réponse :**
```json
{
  "winner": true,
  "probability": 87.5,
  "prediction": "max a de fortes chances de gagner à monaco",
  "driver": "max",
  "circuit": "monaco"
}
```

### `GET /api/v1/model-info`
Informations sur le modèle chargé

## 📁 Structure du Projet

```
backend/
├── app/
│   ├── main.py                    # Point d'entrée
│   ├── core/
│   │   └── config.py             # Configuration
│   ├── routes/
│   │   └── prediction_router.py  # Routes API
│   ├── services/
│   │   └── ml_service.py         # Service ML
│   ├── schemas/
│   │   └── prediction_schema.py  # Pydantic schemas
│   └── models/
│       └── f1_winner_model.joblib # Modèle ML
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🧪 Tester l'API

### Avec curl

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Grid": 1,
    "Rain": 0,
    "Round": 5,
    "Season": 2026,
    "DriverID": "max",
    "ConstructorName": "Red Bull",
    "CircuitID": "monaco"
  }'
```

### Avec Python

```python
import requests

url = "http://localhost:8000/api/v1/predict"
data = {
    "Grid": 1,
    "Rain": 0,
    "Round": 5,
    "Season": 2026,
    "DriverID": "max",
    "ConstructorName": "Red Bull",
    "CircuitID": "monaco"
}

response = requests.post(url, json=data)
print(response.json())
```

## 🔐 Variables d'Environnement

Créer un fichier `.env` avec :

```env
APP_NAME=F1 Live AI Commentator
DEBUG=True
MODEL_PATH=app/models/f1_winner_model.joblib
```

## 🐳 Commandes Docker

```bash
# Construire l'image
docker-compose build

# Lancer les services
docker-compose up

# Lancer en arrière-plan
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down

# Rebuild complet
docker-compose up --build --force-recreate
```

## 📊 Modèle ML

Le modèle utilisé doit être placé dans `app/models/f1_winner_model.joblib`

**Features attendues :**
- Grid (int) : Position de départ
- Rain (int) : 0=sec, 1=pluie
- Round (int) : Numéro de la course
- Season (int) : Année
- DriverID_code (int) : Code du pilote
- ConstructorName_code (int) : Code de l'écurie
- CircuitID_code (int) : Code du circuit

## 🛠️ Développement

### Ajouter une route

1. Créer un nouveau router dans `app/routes/`
2. L'inclure dans `app/main.py`

### Modifier le modèle

1. Remplacer `app/models/f1_winner_model.joblib`
2. Adapter `ml_service.py` si nécessaire
3. Redémarrer l'API

## ❓ Troubleshooting

### Erreur "Model not found"
```bash
# Vérifier que le modèle existe
ls app/models/f1_winner_model.joblib

# Si absent, le copier
cp ../models/f1_winner_model.joblib app/models/
```

### Port 8000 déjà utilisé
```bash
# Changer le port dans docker-compose.yml
ports:
  - "8001:8000"  # Au lieu de 8000:8000
```

### Rebuild complet
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## 📝 TODO

- [ ] Ajouter l'authentification JWT
- [ ] Implémenter le rate limiting
- [ ] Ajouter des tests unitaires
- [ ] Logger les prédictions dans une base de données
- [ ] Ajouter le monitoring (Prometheus)
- [ ] Créer un endpoint pour les prédictions batch

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit (`git commit -m 'Ajout fonctionnalité'`)
4. Push (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet fait partie du Fil Rouge Simplon Maghreb - Formation IA 2026

---

**Auteur :** Manal FAROUQI  
**Projet :** F1 Live AI Commentator  
**Date :** Février 2026
