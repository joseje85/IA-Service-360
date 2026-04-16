import re
from app.rag.vector_store import get_vector_db

_db_instance = None


def get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = get_vector_db()
    return _db_instance


# ==============================
# 🧠 UTILIDADES
# ==============================

def extract_article_number(question: str):
    match = re.search(r"art[íi]culo\s+(\d+)", question.lower())
    return match.group(1) if match else None


def extract_document_type(question: str):
    q = question.lower()

    if "ley de ingresos" in q:
        return "ingresos"

    if "guanajuato" in q:
        return "guanajuato"

    if "reglamento" in q:
        return "reglamento"

    if "codigo" in q:
        return "codigo"

    if "ley" in q:
        return "ley"

    return None


# ==============================
# 🔍 SEARCH POR ARTÍCULO (PRO)
# ==============================

def search_by_article(question: str):
    db = get_db()

    article_number = extract_article_number(question)
    document_type = extract_document_type(question)

    if not article_number:
        return None

    # 🔥 traer chunks del artículo
    results = db.similarity_search(
        question,  # 🔥 IMPORTANTE → usar la pregunta
        k=5,
        filter={"articulo": article_number}
    )

    if not results:
        return None

    # 🔥 ranking semántico natural (ya viene del embedding)
    if document_type:
        results = [
            doc for doc in results
            if document_type in doc.metadata.get("documento", "").lower()
        ] or results

    # 🔥 SI SOLO HAY UNO → directo
    if len(results) == 1:
        doc = results[0]
        return {
            "tipo": "ARTICULO",
            "fuente": doc.metadata.get("source"),
            "contenido": doc.page_content
        }

    # 🔥 MULTI (pero ya limpio)
    return {
        "tipo": "MULTI_ARTICULO",
        "resultados": [
            {
                "fuente": doc.metadata.get("source"),
                "contenido": doc.page_content
            }
            for doc in results[:3]
        ]
    }


# ==============================
# 🔍 SEARCH POR CONTEXTO (PRO)
# ==============================

def search_context(question: str, k=5):
    db = get_db()

    results = db.similarity_search_with_score(question, k=8)

    q = question.lower()

    def score(doc, base_score):
        text = doc.page_content.lower()
        source = doc.metadata.get("source", "").lower()

        score = -base_score  # menor score = mejor en chroma

        # 🔥 boost semántico general (NO hardcode)
        if any(word in text for word in q.split()):
            score += 5

        # 🔥 boost por coincidencia fuerte
        if "licencia" in q and "licencia" in text:
            score += 5

        if "tarifa" in q and "tarifa" in text:
            score += 5

        # 🔥 boost por documento fiscal relevante
        if any(x in source for x in ["ingresos", "fiscal", "hacienda"]):
            score += 10

        # 🔥 penalizar ruido
        if any(x in source for x in ["transparencia", "administrativas"]):
            score -= 10

        return score

    ranked = sorted(
        [(doc, score(doc, base)) for doc, base in results],
        key=lambda x: x[1],
        reverse=True
    )

    return [
        {
            "contenido": doc.page_content,
            "fuente": doc.metadata.get("source", "desconocido")
        }
        for doc, _ in ranked[:3]
    ]


# ==============================
# 🔍 SEARCH POR SOURCE (FOLLOW-UP)
# ==============================

def search_article_in_source(article_number: int, source_hint: str = None):
    db = get_db()

    results = db.similarity_search(
        "",
        k=5,
        filter={"articulo": str(article_number)}
    )

    if not results:
        return None

    if source_hint:
        source_hint = source_hint.lower()

        for doc in results:
            if source_hint in doc.metadata.get("source", "").lower():
                return {
                    "tipo": "ARTICULO",
                    "fuente": doc.metadata.get("source"),
                    "contenido": doc.page_content
                }

    doc = results[0]

    return {
        "tipo": "ARTICULO",
        "fuente": doc.metadata.get("source"),
        "contenido": doc.page_content
    }


# ==============================
# 🔍 SEARCH POR TÍTULO (OPCIONAL)
# ==============================

def extract_topic(question: str):
    q = question.lower()

    keywords = [
        "duración",
        "requisitos",
        "facultades",
        "funciones",
        "nombramiento"
    ]

    for k in keywords:
        if k in q:
            return k

    return None


def search_by_title(question: str):
    db = get_db()

    topic = extract_topic(question)

    if not topic:
        return None

    results = db.similarity_search(question, k=3)

    matches = []

    for doc in results:
        titulo = doc.metadata.get("titulo", "").lower()

        if topic in titulo:
            matches.append({
                "fuente": doc.metadata.get("source"),
                "contenido": doc.page_content,
                "titulo": doc.metadata.get("titulo")
            })

    return matches if matches else None