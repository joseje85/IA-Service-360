from fastapi import FastAPI
from app.routes import rag_routes, ia_routes
from app.services.ollama_service import generate_response
from app.routes import direcciones_routes

app = FastAPI()

# WARMUP DEL MODELO
@app.on_event("startup")
def warmup():
    print("🔥 WARMUP OLLAMA...")
    try:
        generate_response("Hola")
        print("✅ Modelo listo")
    except Exception as e:
        print("❌ Error en warmup:", e)

app.include_router(rag_routes.router)
app.include_router(ia_routes.router)
app.include_router(direcciones_routes.router)