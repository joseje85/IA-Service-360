from fastapi import APIRouter
from app.services.rag_service import search_context
from app.rag.ingest import process_and_store

router = APIRouter()

@router.post("/rag/ingest")
def ingest():
    total = process_and_store()
    return {"mensaje": f"{total} fragmentos procesados"}

@router.post("/rag/ask")
def ask(question: str):
    respuesta = search_context(question)
    return {"respuesta": respuesta}