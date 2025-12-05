import eel
import hashlib
import mysql.connector
import project_manager as pm

from project_manager import update_project_status, get_projects, get_all_projects

for p in get_all_projects(): 
    update_project_status(p["id"])

def get_connection():
    """Membuat koneksi ke database MySQL"""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="project_tracker"
    )

def hash_password(password):
    """Mengubah password menjadi hash SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


@eel.expose
def register(username, password):
    """Registrasi user baru"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return {"success": False, "message": "Username sudah digunakan!"}

    hashed = hash_password(password)
    cur.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed)
    )
    conn.commit()

    cur.close()
    conn.close()
    return {"success": True, "message": "Registrasi berhasil!"}


@eel.expose
def login(username, password):
    """Login user"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    hashed = hash_password(password)
    cur.execute(
        "SELECT * FROM users WHERE username = %s AND password = %s",
        (username, hashed),
    )
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user:
        return {"success": True, "message": "Login berhasil!", "user_id": user["id"]}
    else:
        return {"success": False, "message": "Username atau password salah!"}

eel.init("web")
eel.expose(pm.get_projects)
eel.expose(pm.add_project)
eel.expose(pm.update_project)
eel.expose(pm.delete_project)
eel.expose(pm.get_project_by_id)
eel.expose(pm.get_tasks_by_project)
eel.expose(pm.add_task)
eel.expose(pm.update_task_status)
eel.expose(pm.delete_task)
eel.expose(pm.get_all_tasks)
eel.expose(pm.fix_datetime)

eel.expose(pm.get_projects_by_month_year)

eel.expose(pm.archive_project)
eel.expose(pm.get_archived_projects)
eel.expose(pm.get_all_projects_by_status)
eel.expose(pm.export_project)
eel.expose(pm.update_task)
eel.expose(pm.get_username)

if __name__ == "__main__":
    print("🚀 Menjalankan TaskSphere Dashboard...")
    eel.start("login.html", size=(1000, 650), block=True)
