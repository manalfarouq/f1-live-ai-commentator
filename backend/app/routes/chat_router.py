# backend/app/routes/chat_router.py
from fastapi import APIRouter
from app.schemas.ChatInput import ChatInput
from app.services.rag.augment import repondre_chat

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("")
async def chat(body: ChatInput):
    """
    Endpoint RAG : reçoit une question, retourne une réponse basée sur le PDF F1.

    Input  : { "question": "string" }
    Output : { "question": "...", "answer": "..." }
    """

    # L'objectif est simple : question → PDF → réponse
    return repondre_chat(question=body.question)