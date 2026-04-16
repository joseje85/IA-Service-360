from app.db.postgres import get_connection

# 🔹 Obtener historial
def get_history(thread_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content
        FROM chat_messages
        WHERE thread_id = %s
        ORDER BY created_at ASC
        LIMIT 10
    """, (thread_id,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


# 🔹 Guardar mensaje
def save_message(thread_id: str, role: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chat_messages (thread_id, role, content)
        VALUES (%s, %s, %s)
    """, (thread_id, role, content))

    conn.commit()
    cursor.close()
    conn.close()