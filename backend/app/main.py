# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.services.rag.indexer import indexer
from .routes import prediction_router, f1_data_router, commentary_router, video_router, chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code exécuté AU DÉMARRAGE
    indexer()
    yield
    # Code exécuté À L'ARRÊT (si besoin de cleanup)


app = FastAPI(title="F1 Live AI Commentator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prediction_router)
app.include_router(f1_data_router)
app.include_router(commentary_router)
app.include_router(video_router)
app.include_router(chat_router.router, prefix="/rag")