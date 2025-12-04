import eel
from db import get_db

@eel.expose
def create_room(roomCode, roomName, hostName, mode, totalQuestions):
    conn = get_db()
    cursor = conn.cursor()
    try:
        mapped_mode = "random" if mode.lower() == "acak" else "ordered"
        cursor.execute(
            "INSERT INTO rooms (roomCode, roomName, hostName, mode, totalQuestions) VALUES (%s, %s, %s, %s, %s)",
            (roomCode, roomName, hostName, mapped_mode, totalQuestions)
        )
        conn.commit()
        return {"success": True, "message": "Room berhasil dibuat"}
    except Exception as err:
        return {"success": False, "message": str(err)}
    finally:
        cursor.close()
        conn.close()


@eel.expose
def get_room_data(roomCode):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM rooms WHERE roomCode = %s", (roomCode,))
        room = cursor.fetchone()
        return room if room else None
    except:
        return None
    finally:
        cursor.close()
        conn.close()


@eel.expose
def add_participant(roomCode, participantName):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO participants (roomCode, participantName) VALUES (%s, %s)", (roomCode, participantName))
        conn.commit()
        return {"success": True}
    except Exception as err:
        if "Duplicate entry" in str(err):
            return {"success": False, "message": "Nama sudah digunakan di room ini"}
        return {"success": False, "message": str(err)}
    finally:
        cursor.close()
        conn.close()


@eel.expose
def get_participants(roomCode):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM participants WHERE roomCode = %s", (roomCode,))
        return cursor.fetchall()
    except:
        return []
    finally:
        cursor.close()
        conn.close()


@eel.expose
def get_room_status(roomCode):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM rooms WHERE roomCode = %s", (roomCode,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


@eel.expose
def update_room_status(roomCode, status):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE rooms SET status = %s WHERE roomCode = %s", (status, roomCode))
        conn.commit()
        return {"success": True}
    except Exception as err:
        return {"success": False, "message": str(err)}
    finally:
        cursor.close()
        conn.close()


@eel.expose
def start_quiz(roomCode):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE rooms SET status = 'started' WHERE roomCode = %s", (roomCode,))
        conn.commit()
        return {"success": True}
    except Exception as err:
        return {"success": False, "message": str(err)}
    finally:
        cursor.close()
        conn.close()


@eel.expose
def save_result(roomCode, participantName, score, correct, wrong):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO results (roomCode, participantName, score, correct, wrong) VALUES (%s, %s, %s, %s, %s)",
            (roomCode, participantName, score, correct, wrong)
        )
        conn.commit()
        return {"success": True}
    except Exception as err:
        return {"success": False, "message": str(err)}
    finally:
        cursor.close()
        conn.close()


@eel.expose
def finish_quiz(roomCode):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE rooms SET status = 'finished' WHERE roomCode = %s", (roomCode,))
        conn.commit()
        return {"success": True}
    except Exception as err:
        return {"success": False, "message": str(err)}
    finally:
        cursor.close()
        conn.close()


@eel.expose
def get_leaderboard(roomCode):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT participantName AS name, score FROM results WHERE roomCode = %s ORDER BY score DESC",
            (roomCode,)
        )
        return cursor.fetchall()
    except:
        return []
    finally:
        cursor.close()
        conn.close()
