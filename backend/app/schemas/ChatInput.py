# backend/app/schemas/ChatInput.py
from pydantic import BaseModel


# L'objectif est simple — question → réponse
class ChatInput(BaseModel):
    question: str