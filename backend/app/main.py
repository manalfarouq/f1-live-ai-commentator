from fastapi import FastAPI

from app.services.rag.indexer import indexer

from .routes import prediction_router, f1_data_router, commentary_router, video_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="F1 Live AI Commentator API")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(prediction_router)
app.include_router(f1_data_router)
app.include_router(commentary_router)
app.include_router(video_router)

@app.on_event("startup")                             
async def startup():                                 
    indexer()  