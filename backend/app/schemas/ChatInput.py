from pydantic import BaseModel
from typing import Optional


class ChatInput(BaseModel):
    """Question libre posée par l'utilisateur dans le chat."""
    question: str
    contexte_course: Optional[dict] = {}   # état de la course en cours si dispo