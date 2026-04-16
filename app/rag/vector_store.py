from langchain_community.vectorstores import Chroma
from app.config.settings import VECTOR_DB_PATH
from app.rag.embeddings import get_embeddings

def get_vector_db():
    embeddings = get_embeddings()

    return Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"}
    )
