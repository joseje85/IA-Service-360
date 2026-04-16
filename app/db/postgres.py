import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        host="172.28.46.24",
        database="recaudacion_ollama",
        user="postgres",
        password="Temporal2026.",
        cursor_factory=RealDictCursor
    )