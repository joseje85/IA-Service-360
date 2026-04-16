import os
import re
import shutil
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_core.documents import Document
from app.config.settings import DOCS_PATH, VECTOR_DB_PATH
from app.rag.vector_store import get_vector_db


def load_documents():
    documents = []

    for file in os.listdir(DOCS_PATH):
        path = os.path.join(DOCS_PATH, file)

        if file.endswith(".pdf"):
            loader = PyPDFLoader(path)
        elif file.endswith(".docx"):
            loader = Docx2txtLoader(path)
        else:
            continue

        documents.extend(loader.load())

    return documents


def merge_documents_by_source(documents):
    merged = {}

    for doc in documents:
        source = doc.metadata.get("source", "desconocido")
        page = doc.metadata.get("page", 0)

        if source not in merged:
            merged[source] = []

        merged[source].append((page, doc.page_content))

    combined_documents = []

    for source, pages in merged.items():
        ordered_pages = [content for _, content in sorted(pages, key=lambda item: item[0])]
        combined_documents.append(
            Document(
                page_content="\n".join(ordered_pages),
                metadata={"source": source}
            )
        )

    return combined_documents


def split_by_articles(text):
    pattern = r"(Artículo\s+(\d+)\.?)"
    matches = list(re.finditer(pattern, text))

    articles = []

    for i, match in enumerate(matches):
        start = match.start()
        articulo_num = match.group(2)

        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        contenido = text[start:end]

        # 🔥 buscar título anterior (máximo 200 chars antes)
        prev_text = text[max(0, start - 200):start]

        titulo_match = re.findall(r"\n([A-ZÁÉÍÓÚÑ][^\n]{5,})\n", prev_text)

        titulo = titulo_match[-1] if titulo_match else ""

        articles.append({
            "numero": articulo_num,
            "texto": contenido.strip(),
            "titulo": titulo.strip()
        })

    return articles


def process_and_store():
    docs = merge_documents_by_source(load_documents())

    if os.path.exists(VECTOR_DB_PATH):
        shutil.rmtree(VECTOR_DB_PATH)

    db = get_vector_db()

    all_chunks = []

    for doc in docs:
        file_name = doc.metadata.get("source", "desconocido")
        texto = doc.page_content
        articulos = split_by_articles(texto)

        for art in articulos:
            items = split_article_into_items(art["texto"])

            for item in items:
                all_chunks.append(
                    Document(
                        page_content=item,
                        metadata={
                            "articulo": art["numero"],
                            "source": file_name,
                            "documento": file_name.lower(),
                            "titulo": art["titulo"]
                        }
                    )
                )

    db.add_documents(all_chunks)
    db.persist()

    return len(all_chunks)

def split_article_into_items(article_text):
    """
    Divide artículo en bloques más grandes para preservar contexto
    """

    # 🔥 si es tabla/tarifa → NO dividir agresivamente
    if "TARIFA" in article_text or "$" in article_text:
        return [article_text]  # 👈 TODO el artículo completo

    # fallback normal
    lines = article_text.split("\n")

    chunks = []
    current = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if re.match(r"^(I|II|III|IV|V|VI|VII|VIII|IX|X)\.", line):
            if current:
                chunks.append(" ".join(current))
                current = []

        current.append(line)

    if current:
        chunks.append(" ".join(current))

    return chunks
