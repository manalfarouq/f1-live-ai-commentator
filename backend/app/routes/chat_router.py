# backend/app/routes/chat_router.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.ChatInput import ChatInput
from app.services.rag.augment import repondre_chat, repondre_chat_stream

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("")
async def chat(body: ChatInput):
    """
    Endpoint RAG existant — inchangé.
    Input  : { "question": "string" }
    Output : { "question": "...", "answer": "..." }
    """
    return repondre_chat(question=body.question)


@router.post("/stream")
async def chat_stream(body: ChatInput):
    """
    Même RAG Gemini, réponse streamée en Server-Sent Events.
    Input  : { "question": "string" }
    Output : text/event-stream
    """
    return StreamingResponse(
        repondre_chat_stream(question=body.question),
        media_type="text/event-stream",
        headers={
            "Cache-Control"    : "no-cache",
            "X-Accel-Buffering": "no",    
        },
    )