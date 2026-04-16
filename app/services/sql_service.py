from app.db.connection import get_connection

def execute_query(query: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query)

        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        results = [dict(zip(columns, row)) for row in rows]

        return results

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()