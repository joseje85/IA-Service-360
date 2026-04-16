from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.services.direcciones_service import procesar_direcciones

router = APIRouter(prefix="/ia", tags=["Direcciones IA"])


class DireccionesRequest(BaseModel):
    rfc: str
    direcciones: List[str]


@router.post("/normalizar-direcciones")
def normalizar_direcciones(data: DireccionesRequest):
    resultado = procesar_direcciones(data.rfc, data.direcciones)
    return resultado