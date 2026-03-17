from fastapi import APIRouter, HTTPException

from app.schemas.ChatInput    import ChatInput
from app.schemas.RaceDataInput import RaceDataInput

from app.services.rag.augment import (
    generer_commentaire,
    generer_tous_personas,
    repondre_chat,
)
from app.services.rag.indexer import indexer

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/commentary")
async def commentary(data: RaceDataInput):
    try:
        race_dict = data.model_dump(exclude_none=True)
        resultat  = generer_commentaire(race_dict, persona=data.persona)
        return {"status": "ok", "data": resultat}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/commentary/all")
async def commentary_all(data: RaceDataInput):
    try:
        race_dict = data.model_dump(exclude_none=True)
        resultats = generer_tous_personas(race_dict)
        return {"status": "ok", "data": resultats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat(data: ChatInput):
    try:
        resultat = repondre_chat(data.question)
        return {"status": "ok", "data": resultat}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index")
async def reindex():
    try:
        collection = indexer()
        if collection is None:
            raise HTTPException(status_code=404, detail="PDF non trouvé dans data/rag/")
        return {"status": "ok", "chunks": collection.count()}
    except Exception as e:
        print(f"[RAG ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))