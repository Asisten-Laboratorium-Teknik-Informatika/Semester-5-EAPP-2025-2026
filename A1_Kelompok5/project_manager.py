import mysql.connector
from datetime import datetime, date
import json
from tkinter import filedialog

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="project_tracker"
    )

def update_project_status(project_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT status FROM tasks WHERE project_id=%s", (project_id,))
    tasks = cur.fetchall()

    statuses = [t["status"] for t in tasks]

    if len(tasks) == 0:
        new_status = "pending"

    elif all(s in ("completed", "done") for s in statuses):
        new_status = "completed"

    elif any(s == "in_progress" for s in statuses):
        new_status = "in_progress"

    else:
        new_status = "pending"

    cur2 = conn.cursor()
    cur2.execute("UPDATE projects SET status=%s WHERE id=%s", (new_status, project_id))
    conn.commit()

    cur.close()
    cur2.close()
    conn.close()


def get_projects(user_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM projects WHERE user_id = %s AND is_archived = 0 ORDER BY created_at DESC", 
        (user_id,)
    )
    projects = cur.fetchall()

    for p in projects:
        if p["start_date"]:
            p["start_date"] = p["start_date"].strftime("%Y-%m-%d")
        if p["end_date"]:
            p["end_date"] = p["end_date"].strftime("%Y-%m-%d")

    cur.close()
    conn.close()
    return projects

def add_project(user_id, name, description, start_date=None, end_date=None):
    now = datetime.now()
    month = now.month
    year = now.year

    if start_date == "":
        start_date = None
    if end_date == "":
        end_date = None

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO projects (user_id, name, description, start_date, end_date, month, year, created_at, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
    """, (user_id, name, description, start_date, end_date, month, year, "pending")) 
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "🆕 Proyek berhasil ditambahkan!"}

def get_project_by_id(project_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
    project = cur.fetchone()
    cur.close()
    conn.close()
    return project

def update_project(project_id, new_name, new_description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE projects SET name = %s, description = %s WHERE id = %s
    """, (new_name, new_description, project_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "✏️ Proyek berhasil diperbarui!"}

def delete_project(project_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE project_id = %s", (project_id,))
    cur.execute("DELETE FROM projects WHERE id = %s", (project_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "🗑️ Proyek & tugas dihapus!"}

def archive_project(project_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE projects SET is_archived = 1 WHERE id = %s
    """, (project_id,))

    conn.commit()
    cur.close()
    conn.close()
    return {"message": "📦 Proyek berhasil diarsipkan!"}

def get_archived_projects(user_id): 
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM projects WHERE user_id = %s AND is_archived = 1 ORDER BY created_at DESC", 
        (user_id,) 
    ) 
    result = cur.fetchall()
    cur.close()
    conn.close()

    for p in result:
        if p.get("start_date"):
            p["start_date"] = p["start_date"].strftime("%Y-%m-%d")
        if p.get("end_date"):
            p["end_date"] = p["end_date"].strftime("%Y-%m-%d")

    return result

def export_project(project_id):
    project = get_project_by_id(project_id)
    tasks = get_tasks_by_project(project_id)

    def fix_dates(obj):
        if isinstance(obj, dict):
            return {k: fix_dates(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [fix_dates(i) for i in obj]
        elif isinstance(obj, (datetime, date)):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return obj

    project = fix_dates(project)
    tasks = fix_dates(tasks)

    data = {
        "project": project,
        "tasks": tasks
    }

    file_path = f"export_project_{project_id}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return {"message": "📂 Export sukses!", "file": file_path}

def fix_datetime(dt):
    if not dt or dt == "":
        return None
    try:
        parsed = datetime.fromisoformat(dt)
        return parsed.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt

def get_tasks_by_project(project_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id, project_id, title, description, status,
                deadline, start_time, end_time
        FROM tasks WHERE project_id = %s
    """, (project_id,))
    tasks = cur.fetchall()

    for t in tasks:
        for key in ["deadline", "start_time", "end_time"]:
            if t[key]:
                t[key] = t[key].strftime("%Y-%m-%d %H:%M:%S")

    cur.close()
    conn.close()
    return tasks

def add_task(project_id, title, description="", deadline=""):
    conn = get_connection()
    cur = conn.cursor()

    if deadline:
        deadline = deadline.replace("T", " ") + ":00"
        cur.execute("""
            INSERT INTO tasks (project_id, title, description, status, deadline)
            VALUES (%s, %s, %s, %s, %s)
        """, (project_id, title, description, "todo", deadline))
    else:
        cur.execute("""
            INSERT INTO tasks (project_id, title, description, status)
            VALUES (%s, %s, %s, %s)
        """, (project_id, title, description, "todo"))

    conn.commit()

    update_project_status(project_id)

    cur.close()
    conn.close()
    return {"message": "🆕 Tugas berhasil ditambahkan!"}

def update_task_status(task_id, new_status):
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if new_status == "in progress":
        cur.execute("""
            UPDATE tasks SET status=%s, start_time=%s WHERE id=%s
        """, (new_status, now, task_id))
    elif new_status == "completed":
        cur.execute("""
            UPDATE tasks SET status=%s, end_time=%s WHERE id=%s
        """, ("completed", now, task_id))
    else:
        cur.execute("""
            UPDATE tasks SET status=%s WHERE id=%s
        """, (new_status, task_id))

    cur.execute("SELECT project_id FROM tasks WHERE id = %s", (task_id,))
    project_id = cur.fetchone()[0]
    update_project_status(project_id)

    conn.commit()
    cur.close()
    conn.close()
    return {"message": "🔄 Status tugas & proyek diperbarui!"}

def delete_task(task_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT project_id FROM tasks WHERE id = %s", (task_id,))
    project_id = cur.fetchone()[0]

    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()

    update_project_status(project_id)

    cur.close()
    conn.close()
    return {"message": "❌ Tugas dihapus & status proyek diperbarui!"}

def get_all_tasks():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()

    for t in tasks:
        for key in ["deadline", "start_time", "end_time"]:
            if t[key]:
                t[key] = t[key].strftime("%Y-%m-%d %H:%M:%S")

    cur.close()
    conn.close()
    return tasks

def get_projects_by_month_year(user_id, month=None, year=None): 
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    query = "SELECT * FROM projects WHERE user_id = %s" 
    params = [user_id]

    if month not in (None, "", "null"):
        month = int(month)
        query += " AND month = %s"
        params.append(month)

    if year not in (None, "", "null"):
        year = int(year)
        query += " AND year = %s"
        params.append(year)

    query += " ORDER BY created_at DESC"

    cur.execute(query, params)
    projects = cur.fetchall()

    for p in projects:
        if p["start_date"]:
            p["start_date"] = p["start_date"].strftime("%Y-%m-%d")
        if p["end_date"]:
            p["end_date"] = p["end_date"].strftime("%Y-%m-%d")

    cur.close()
    conn.close()
    return projects

def get_all_projects_by_status(status):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM projects WHERE status = %s", (status,))
    projects = cur.fetchall()
    cur.close()
    conn.close()
    return projects

def get_all_projects():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id FROM projects") 
    projects = cur.fetchall()
    cur.close()
    conn.close()
    return projects

def update_task(task_id, new_title, new_description, new_start=None, new_end=None):
    conn = get_connection()
    cur = conn.cursor()

    new_start = fix_datetime(new_start)
    new_end = fix_datetime(new_end)

    cur.execute("""
        UPDATE tasks 
        SET title=%s, description=%s, start_time=%s, end_time=%s
        WHERE id=%s
    """, (new_title, new_description, new_start, new_end, task_id))
    conn.commit()

    cur.execute("SELECT project_id FROM tasks WHERE id = %s", (task_id,))
    project_id = cur.fetchone()[0]
    update_project_status(project_id)

    cur.close()
    conn.close()

    return {"message": "✏️ Tugas diperbarui & tanggal tersimpan dengan benar!"}



def get_username(user_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["username"] if row else "Unknown"
