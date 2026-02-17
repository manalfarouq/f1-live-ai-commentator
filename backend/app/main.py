from fastapi import FastAPI

from .routes import prediction_router, f1_data_router
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
app.include_router(prediction_router.router)
app.include_router(f1_data_router.router)
