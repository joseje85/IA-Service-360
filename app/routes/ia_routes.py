from fastapi import APIRouter
from app.services.hybrid_service import hybrid_query
import uuid

router = APIRouter()

@router.post("/ia/preguntar")
def preguntar(question: str, thread_id: str = None):

    # 🔥 Si no viene thread → crear uno nuevo
    if not thread_id:
        thread_id = str(uuid.uuid4())

    result = hybrid_query(question, thread_id)

    return {
        "thread_id": thread_id,
        "data": result
    }
