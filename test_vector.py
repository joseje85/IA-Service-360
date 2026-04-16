from app.rag.vector_store import get_vector_db

db = get_vector_db()

results = db.similarity_search("cual seria el precio o tarifa por el otorgamiento de una licencia de alcoholes tipo B1?", k=5)

for r in results:
    print("----")
    print(r.page_content)