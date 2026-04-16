import os
from dotenv import load_dotenv

load_dotenv(".env")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "data")
DOCS_PATH = os.path.join(DATA_PATH, "documentos")
VECTOR_DB_PATH = os.path.join(DATA_PATH, "vector_db")

PORT = int(os.getenv("PORT", 8001))
DEBUG = os.getenv("DEBUG", "True") == "True"
WORKERS = int(os.getenv("WORKERS", 1))
EMBEDDINGS_LOCAL_ONLY = os.getenv("EMBEDDINGS_LOCAL_ONLY", "True") == "True"

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen:7b")

POSTGRES_URL = os.getenv("POSTGRES_URL")
SQLSERVER_CONN = os.getenv("SQLSERVER_CONN")
