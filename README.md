# 🏎️ F1 Live AI Commentator

<div align="center">

![F1 AI Banner](https://img.shields.io/badge/F1-Live%20AI%20Commentator-e8001d?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0tMiAxNWwtNS01IDEuNDEtMS40MUwxMCAxNC4xN2w3LjU5LTcuNTlMMTkgOGwtOSA5eiIvPjwvc3ZnPg==)

[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61dafb?style=flat-square&logo=react&logoColor=black)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ed?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![LightGBM](https://img.shields.io/badge/LightGBM-v2-brightgreen?style=flat-square)](https://lightgbm.readthedocs.io)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-4285f4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

**Système d'analyse de course F1 en temps réel combinant Vision par Ordinateur, Machine Learning et Commentaires LLM multi-agents avec RAG.**

[🚀 Démarrage rapide](#-démarrage-rapide) · [📖 Documentation API](#-documentation-api) · [🧠 Modèle ML](#-modèle-ml) · [🏗️ Architecture](#️-architecture)

</div>

---

## 📋 Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#️-architecture)
- [Stack technique](#-stack-technique)
- [Démarrage rapide](#-démarrage-rapide)
- [Structure du projet](#-structure-du-projet)
- [Modèle ML](#-modèle-ml)
- [Système RAG](#-système-rag)
- [Documentation API](#-documentation-api)
- [Tests](#-tests)
- [Variables d'environnement](#-variables-denvironnement)

---

## 🎯 Vue d'ensemble

**F1 Live AI Commentator** est un système d'intelligence artificielle de bout en bout qui analyse les courses de Formule 1 en temps réel. Il combine plusieurs briques IA pour produire des commentaires intelligents et des prédictions de résultats.

### Ce que fait le système

| Étape | Description |
|-------|-------------|
| 👁️ **Voir** | YOLOv8 détecte les drapeaux, accidents et arrêts aux stands depuis la vidéo |
| 📊 **Comprendre** | OCR extrait les positions, temps au tour et écarts depuis les graphiques TV |
| 🤖 **Prédire** | Modèle LightGBM entraîné sur 26 saisons prédit le Top 3 |
| 🗣️ **Commenter** | 4 agents LLM génèrent des commentaires depuis 4 perspectives différentes |
| 📚 **Expliquer** | RAG sur le règlement F1 2025 répond aux questions des utilisateurs |

---

## ✨ Fonctionnalités

### 🎥 Vision par ordinateur
- Détection automatique de drapeaux (jaune, rouge, vert, damier) via YOLOv8
- Extraction OCR des données de course depuis les retransmissions TV
- Suivi des arrêts aux stands et détection d'incidents

### 🤖 Machine Learning
- Prédiction de position finale avec **MAE = 1.33** et **R² = 0.86**
- Entraîné sur **26 saisons** de données F1 (1998–2023)
- 3 modèles comparés : LightGBM ✅, XGBoost, Random Forest
- **43 features** incluant rythme, position, stratégie pit-stop

### 🗣️ Commentaires IA multi-agents
- **4 personas** : Journaliste, Professeur, Ingénieur, Fan
- Génération en temps réel via **Gemini 2.5 Flash**
- Latence < 500ms par commentaire

### 📚 Chat RAG (Règlement F1)
- Base de connaissances vectorielle sur le règlement F1 2025
- Recherche sémantique via **ChromaDB** + embeddings `all-MiniLM-L6-v2`
- Réponses contextuelles en 2–4 phrases

### 🖥️ Interface temps réel
- Dashboard React avec mise à jour live
- Timeline interactive par tour
- Graphique d'évolution de probabilité de victoire

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│         Dashboard · Chat RAG · Timeline · Charts         │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP REST
┌─────────────────────────▼───────────────────────────────┐
│                   BACKEND (FastAPI)                      │
│  /predict  /rag/chat  /rag/commentary  /video/analyze    │
└──────┬──────────┬──────────────┬───────────────┬────────┘
       │          │              │               │
┌──────▼──┐  ┌────▼────┐  ┌─────▼──────┐  ┌────▼───────┐
│  ML     │  │  RAG    │  │  LLM       │  │  Vision    │
│ Service │  │ Service │  │  Service   │  │  Service   │
│LightGBM │  │ChromaDB │  │Gemini 2.5  │  │YOLOv8+OCR  │
└─────────┘  └────┬────┘  └────────────┘  └────────────┘
                  │
            ┌─────▼─────┐
            │ PDF F1    │
            │ Règlement │
            └───────────┘
```

---

## 🛠️ Stack technique

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **Backend** | FastAPI 0.110+ | API REST |
| **ML** | LightGBM, XGBoost, scikit-learn | Prédiction de position |
| **LLM** | Gemini 2.5 Flash | Génération de commentaires |
| **RAG** | ChromaDB + SentenceTransformers | Base de connaissances F1 |
| **Vision** | YOLOv8 + EasyOCR | Analyse vidéo |
| **Frontend** | React 18 + Vite | Interface utilisateur |
| **Base de données** | PostgreSQL 15 | Stockage données course |
| **Conteneurisation** | Docker Compose | Déploiement |

---

## 🚀 Démarrage rapide

### Prérequis

- Docker & Docker Compose
- Clé API Gemini ([obtenir ici](https://ai.google.dev))
- Python 3.11+ (pour le développement local)

### Avec Docker (recommandé)

```bash
# 1. Cloner le dépôt
git clone https://github.com/yourusername/f1-live-ai-commentator.git
cd f1-live-ai-commentator

# 2. Configurer les variables d'environnement
cp .env.example .env
# Remplir GEMINI_API_KEY dans .env

# 3. Déposer le PDF du règlement F1
# → data/rag/f1_regles.pdf

# 4. Lancer tous les services
docker compose up

# 5. Accéder à l'application
# Frontend  : http://localhost:3000
# API docs  : http://localhost:8001/docs
```

### Sans Docker (développement local)

```bash
# Backend
cd backend
uv sync                          # ou pip install -r requirements.txt
uv run python -c "from app.services.rag.indexer import indexer; indexer()"
uvicorn app.main:app --reload --port 8001

# Frontend (autre terminal)
cd frontend
npm install
npm run dev
```

---

## 📁 Structure du projet

```
f1-live-ai-commentator/
│
├── backend/
│   └── app/
│       ├── core/
│       │   └── config.py              # Settings Pydantic
│       ├── routes/
│       │   ├── prediction_router.py   # POST /predict
│       │   ├── commentary.py          # POST /rag/commentary
│       │   ├── chat_router.py         # POST /chat
│       │   └── video_router.py        # POST /video/analyze
│       ├── services/
│       │   ├── ml_service.py          # Prédiction LightGBM
│       │   ├── llm_service.py         # Génération Gemini
│       │   ├── vision_service.py      # YOLOv8 + OCR
│       │   ├── video_service.py       # Pipeline vidéo
│       │   └── rag/
│       │       ├── indexer.py         # PDF → ChromaDB
│       │       ├── retriever.py       # Recherche sémantique
│       │       └── augment.py         # Génération avec contexte
│       ├── schemas/                   # Modèles Pydantic
│       └── main.py                    # Point d'entrée FastAPI
│
├── frontend/
│   └── src/
│       └── F1Dashboard.jsx            # Dashboard principal
│
├── data/
│   ├── rag/
│   │   ├── f1_regles.pdf              # Règlement F1 (à déposer)
│   │   └── chroma_db/                 # Base vectorielle (auto-générée)
│   └── processed/
│       └── training_dataset.csv       # Données d'entraînement
│
├── models/
│   ├── f1_winner_model.joblib         # Modèle LightGBM v5
│   └── feature_names_v2.pkl           # Noms des 43 features
│
├── notebooks/
│   └── train_model.ipynb              # Entraînement et comparaison
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🧠 Modèle ML

### Problème

Prédire la **position finale** d'un pilote à chaque tour de course (régression), puis convertir en probabilité de **Top 3** (classification avec seuil optimal).

### Données

| Caractéristique | Valeur |
|-----------------|--------|
| Source | Ergast API + OpenF1 |
| Période | 1998 – 2023 (26 saisons) |
| Courses | 10 398 |
| Split | Train ≤ 2019 / Val 2020–2021 / Test ≥ 2022 |

> ⚠️ **Split temporel** — on ne mélange jamais les années pour éviter le data leakage. Un modèle entraîné sur 2022 et évalué sur 2019 serait de la triche.

### Features (43 au total)

| Catégorie | Features |
|-----------|----------|
| **Rythme** | `lap_time_delta`, `pace_vs_best`, `consistency`, `pace_gap_to_leader` |
| **Position** | `current_position`, `position_momentum`, `overtake_opportunity`, `late_top5` |
| **Course** | `race_progress_pct`, `is_early_race`, `is_mid_race`, `is_late_race`, `laps_remaining` |
| **Stratégie** | `nb_pit_stops`, `has_pitted`, `pit_frequency`, `recovery_potential` |

### Sample Weights

Pour que le modèle accorde plus d'importance aux informations de fin de course :

```
poids = (1.0 + 2.0 × race_progress_pct) × bonus_top3
```

- Tour 1/60  → poids ≈ 1.0
- Tour 60/60 → poids ≈ 3.0
- Pilote Top 3 → ×2 supplémentaire

### Résultats

| Modèle | MAE ↓ | RMSE ↓ | R² ↑ |
|--------|-------|--------|------|
| **LightGBM v5** ✅ | **1.33** | — | **0.86** |
| XGBoost | ~1.4 | — | ~0.84 |
| Random Forest | ~1.6 | — | ~0.80 |

> **MAE = 1.33** signifie que le modèle se trompe en moyenne de **1.33 place** sur la position finale.

### Hyperparamètre tuning

Méthode : `RandomizedSearchCV` avec 30 itérations et cross-validation à 3 folds sur un sous-échantillon de 100 000 lignes (pour la rapidité), puis entraînement final sur l'intégralité du train set.

---

## 📚 Système RAG

Le système RAG (Retrieval-Augmented Generation) permet de répondre aux questions sur le règlement F1 en s'appuyant sur le PDF officiel.

### Pipeline

```
PDF F1 (f1_regles.pdf)
    ↓ pdfplumber (extraction texte)
    ↓ Découpage en chunks (500 chars, overlap 80)
    ↓ Embeddings all-MiniLM-L6-v2
    ↓ Stockage ChromaDB
         ↓
Question utilisateur
    ↓ Embedding de la question
    ↓ Recherche des 3 chunks les plus proches
    ↓ Prompt : contexte + question → Gemini 2.5 Flash
    ↓ Réponse en 2-4 phrases
```

### Exemple

```
Question : "Que signifie un drapeau jaune ?"

Réponse : "Un drapeau jaune signifie qu'il y a un danger sur ou à côté
de la piste. Dans cette zone, les dépassements sont strictement interdits
pour les pilotes. C'est une mesure de sécurité essentielle."
```

---

## 📖 Documentation API

Une fois le serveur lancé, la documentation interactive est disponible sur :
- **Swagger UI** : http://localhost:8001/docs
- **ReDoc** : http://localhost:8001/redoc

### Endpoints principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/v1/predict` | Prédiction de position ML |
| `POST` | `/rag/commentary` | Commentaire live avec persona |
| `POST` | `/rag/commentary/all` | Commentaires des 4 personas |
| `POST` | `/chat` | Question → RAG → réponse |
| `POST` | `/video/analyze` | Analyse d'une vidéo de course |
| `GET` | `/video/status/{job_id}` | Statut d'une analyse en cours |
| `GET` | `/health` | Santé de l'API |

### Exemple : prédiction

```bash
curl -X POST http://localhost:8001/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "lap": 42,
    "current_position": 2,
    "race_progress_pct": 70,
    "last_lap_time_ms": 92000
  }'
```

```json
{
  "position_predite": 2,
  "probability": 73.5,
  "is_top3": true
}
```

### Exemple : chat RAG

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Que signifie un drapeau jaune ?"}'
```

```json
{
  "question": "Que signifie un drapeau jaune ?",
  "answer": "Un drapeau jaune indique un danger sur la piste..."
}
```

---

## 🧪 Tests

```bash
# Tester l'indexation RAG
cd backend
uv run python -c "from app.services.rag.indexer import indexer; indexer()"

# Tester le retriever
uv run python -c "
from app.services.rag.retriever import retriever
chunks = retriever('drapeau jaune')
for i, c in enumerate(chunks): print(f'Chunk {i+1}:', c[:150])
"

# Tester le flow complet RAG
uv run python -c "
from app.services.rag.augment import repondre_chat
print(repondre_chat('Que signifie un drapeau jaune ?'))
"

# Lancer l'API et tester via Swagger
uvicorn app.main:app --reload
# → http://localhost:8001/docs
```

---

## 🔐 Variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
# API Keys
GEMINI_API_KEY=your_gemini_key_here
HF_TOKEN=your_hf_token_here          # optionnel, évite les rate limits

# Base de données
POSTGRES_USER=f1user
POSTGRES_PASSWORD=f1password
POSTGRES_DB=f1_predictions
DATABASE_URL=postgresql://f1user:f1password@db:5432/f1_predictions

# Modèle ML
MODEL_PATH=app/models/f1_winner_model.joblib

# Sécurité
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# RAG (chemins absolus dans Docker)
F1_PDF_PATH=/app/data/rag/f1_regles.pdf
CHROMA_DIR=/app/data/rag/chroma_db
CHUNK_SIZE=500
CHUNK_OVERLAP=80
EMBED_MODEL=all-MiniLM-L6-v2
```

---

## 🤝 Contribution

1. Fork le projet
2. Créer une branche : `git checkout -b feature/ma-feature`
3. Commit : `git commit -m 'feat: description claire'`
4. Push : `git push origin feature/ma-feature`
5. Ouvrir une Pull Request

---


<div align="center">

**Auteure :** Manal FAROUQI  
**Formation :** Simplon Maghreb — Spécialisation IA 2026  
**Projet :** Fil Rouge — F1 Live AI Commentator

</div>