import eel
from db import get_db

@eel.expose
def add_question(roomCode, qText, qType, qScore, options, correct):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO questions (roomCode, qText, qType, qScore, options, correct)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (roomCode, qText, qType, qScore, options, correct))
        conn.commit()
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        cursor.close()
        conn.close()


@eel.expose
def get_questions(roomCode):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM questions WHERE roomCode = %s", (roomCode,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


@eel.expose
def delete_question(qId):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id = %s", (qId,))
    conn.commit()
    cursor.close()
    conn.close()
    return True
