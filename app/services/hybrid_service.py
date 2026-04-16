from app.services.ollama_service import generate_response
from app.services.sql_service import execute_query
from app.services.rag_service import search_context, search_by_article
from app.services.memory_service import get_history, save_message
import re


# ==============================
# 🧠 DETECTAR INTENCIÓN
# ==============================
def detect_intent(question: str):
    q = question.lower()

    if any(k in q for k in ["cuántos", "total", "conteo", "suma", "promedio"]):
        return "SQL"

    return "RAG"


# ==============================
# 🧠 HISTORIAL
# ==============================
def normalize_history(history):
    normalized = []

    for m in history:
        if isinstance(m, dict):
            role = m.get("role")
            content = m.get("content")
        elif isinstance(m, (list, tuple)):
            role = m[0] if len(m) > 0 else None
            content = m[1] if len(m) > 1 else None
        else:
            continue

        if role and content:
            normalized.append({
                "role": role,
                "content": content
            })

    return normalized


# ==============================
# 🧠 CONTEXTUALIZAR PREGUNTA
# ==============================
def build_contextual_question(question, history):

    if not history:
        return question

    history_text = "\n".join([
        f"{m['role']}: {m['content']}"
        for m in history[-4:]
    ])

    prompt = f"""
Reformula la pregunta usando el contexto del historial.

Reglas:
- Mantén intención original
- Incluye contexto importante (ej: B1, otorgamiento, etc.)
- NO respondas
- SOLO devuelve la pregunta mejorada

Historial:
{history_text}

Pregunta:
{question}

Nueva pregunta:
"""

    nueva = generate_response(prompt, temperature=0)

    if len(nueva) > 200:
        return question

    return nueva.strip()


# ==============================
# 🧠 SEÑALES DEL HISTORIAL
# ==============================
def enrich_with_history_signals(question, history):
    q = question.lower()

    if "otorgamiento" in q:
        return question

    for m in reversed(history):
        content = m["content"].lower()

        if "otorgamiento" in content:
            return question + " otorgamiento"

    return question


# ==============================
# 🧠 RESPUESTA CON CONTEXTO
# ==============================
def answer_with_context(question: str, context: str):

    if not context or len(context.strip()) < 50:
        return "No se encontró la respuesta exacta en el contexto"

    prompt = f"""
Eres un asistente legal especializado en normativa de México.

INSTRUCCIONES CRÍTICAS:
- Responde SOLO con información del contexto.
- NO inventes información.
- Identifica coincidencias EXACTAS entre la pregunta y el contexto.
- Si hay múltiples montos:
    1. Muestra primero el que coincide exactamente con la pregunta
    2. Después muestra otros montos relacionados
- NO ignores información relevante.
- Máximo 5 líneas.

Pregunta:
{question}

Contexto:
{context}

Respuesta:
"""

    return generate_response(prompt, temperature=0.05, num_predict=200).strip()


# ==============================
# 🚀 MOTOR PRINCIPAL
# ==============================
def hybrid_query(question: str, thread_id: str = None):

    history = normalize_history(get_history(thread_id)) if thread_id else []
    print("HISTORY RAW:", history)

    # 🔥 CONTEXTO REAL
    retrieval_question = build_contextual_question(question, history)
    retrieval_question = enrich_with_history_signals(retrieval_question, history)

    print("🧠 QUESTION:", retrieval_question)

    if thread_id:
        save_message(thread_id, "user", question)

    intent = detect_intent(retrieval_question)

    # ================= SQL =================
    if intent == "SQL":
        sql = generate_response(f"Genera SQL:\n{retrieval_question}")
        result = execute_query(sql)

        if thread_id:
            save_message(thread_id, "assistant", str(result))

        return {"tipo": "SQL", "resultado": result}

    # ================= RAG =================
    direct_result = search_by_article(retrieval_question)

    # 🔥 ARTÍCULO DIRECTO
    if direct_result and direct_result["tipo"] == "ARTICULO":

        contenido = direct_result["contenido"]
        fuente = direct_result.get("fuente", "desconocido")

        contexto = f"Fuente: {fuente}\n{contenido}"

        respuesta = answer_with_context(retrieval_question, contexto)

        print("📚 RESULTADOS:", [contenido])
        print("📄 CONTEXTO:", contexto)

        if thread_id:
            save_message(thread_id, "assistant", respuesta)

        return {
            "tipo": "RAG_ARTICULO",
            "respuesta": respuesta
        }

    # ================= RAG GENERAL =================
    resultados = search_context(retrieval_question)

    if not resultados:
        respuesta = "No se encontró información relevante en la base de conocimiento."

        if thread_id:
            save_message(thread_id, "assistant", respuesta)

        return {
            "tipo": "SIN_CONTEXTO",
            "respuesta": respuesta
        }

    contexto = "\n\n".join([
        f"Fuente: {r['fuente']}\n{r['contenido']}"
        for r in resultados[:3]
    ])

    respuesta = answer_with_context(retrieval_question, contexto)

    print("📚 RESULTADOS:", resultados)
    print("📄 CONTEXTO:", contexto)

    if thread_id:
        save_message(thread_id, "assistant", respuesta)

    return {
        "tipo": "RAG",
        "respuesta": respuesta
    }