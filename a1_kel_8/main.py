import eel
import pymysql
from pymysql.cursors import DictCursor
from datetime import datetime, date
import hashlib
import sys, os

# ====================================
# PyMySQL Setup (EXE Friendly)
# ====================================
pymysql.install_as_MySQLdb()


# ====================================
# Resource Path for backend files (NOT for web folder)
# ====================================
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# ====================================
# INIT FRONTEND (IMPORTANT!)
# DO NOT USE resource_path HERE
# ====================================
eel.init("web")


current_user = None


# ====================================
# DATABASE CONNECTION USING PyMySQL
# ====================================
def create_connection():
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="manajemen_kadaluarsa",
            cursorclass=DictCursor
        )
        print("✅ Koneksi PyMySQL berhasil!")
        return connection
    except Exception as e:
        print("❌ Gagal konek ke DB:", e)
        return None


# ====================================
# USER SECTION
# ====================================
@eel.expose
def register_user(name, email, password):
    connection = create_connection()
    if connection is None:
        return "db_error"

    cursor = connection.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()

    query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
    cursor.execute(query, (name, email, hashed_pw))
    connection.commit()

    cursor.close()
    connection.close()

    print("🟢 Registrasi berhasil:", email)
    return "success"


@eel.expose
def login_user(email, password):
    global current_user

    connection = create_connection()
    if connection is None:
        return "db_error"

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if not user:
        print("❌ Email tidak ditemukan:", email)
        return "not_found"

    hashed_pw = hashlib.sha256(password.encode()).hexdigest()

    if hashed_pw != user["password"]:
        print("❌ Password salah untuk:", email)
        return "wrong_password"

    current_user = email
    print("✅ Login berhasil:", email)
    return "success"


@eel.expose
def update_profile(email, name):
    connection = create_connection()
    if connection is None:
        return "db_error"

    cursor = connection.cursor()
    cursor.execute("UPDATE users SET name=%s WHERE email=%s", (name, email))
    connection.commit()

    cursor.close()
    connection.close()
    print("🟢 Profil diupdate:", email)
    return "success"


# ====================================
# FOOD SECTION
# ====================================
@eel.expose
def get_foods_by_user():
    global current_user
    if not current_user:
        return []

    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM foods WHERE user_email=%s ORDER BY id DESC",
        (current_user,)
    )
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    # Format waktu
    for row in rows:
        if isinstance(row.get("tanggal_dibuat"), datetime):
            row["tanggal_dibuat"] = format_datetime(row["tanggal_dibuat"])
        if isinstance(row.get("tanggal_edit"), datetime):
            row["tanggal_edit"] = format_datetime(row["tanggal_edit"])
        if isinstance(row.get("tanggal_expired"), date):
            row["tanggal_expired"] = format_date(row["tanggal_expired"])
        if isinstance(row.get("created_at"), datetime):
            row["created_at"] = format_datetime(row["created_at"])
        if isinstance(row.get("updated_at"), datetime):
            row["updated_at"] = format_datetime(row["updated_at"])

    print("📦 Data makanan user dikirim:", current_user)
    return rows


@eel.expose
def add_food(nama_makanan, jumlah, tanggal_expired):
    global current_user
    if not current_user:
        return "not_logged_in"

    connection = create_connection()
    if connection is None:
        return "db_error"

    cursor = connection.cursor()

    query = """
        INSERT INTO foods (user_email, nama_makanan, jumlah, tanggal_dibuat, tanggal_expired, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), %s, NOW(), NOW())
    """

    cursor.execute(query, (current_user, nama_makanan, jumlah, tanggal_expired))
    connection.commit()

    cursor.close()
    connection.close()

    print("🟢 Food added:", nama_makanan)
    return "success"


@eel.expose
def get_food_by_id(food_id):
    global current_user
    if not current_user:
        return None

    connection = create_connection()
    if connection is None:
        return None

    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM foods WHERE id=%s AND user_email=%s",
        (food_id, current_user)
    )
    food = cursor.fetchone()

    cursor.close()
    connection.close()

    return food


@eel.expose
def update_food(food_id, nama_makanan, jumlah, tanggal_expired):
    global current_user
    if not current_user:
        return "not_logged_in"

    connection = create_connection()
    if connection is None:
        return "db_error"

    cursor = connection.cursor()

    query = """
        UPDATE foods
        SET nama_makanan=%s, jumlah=%s, tanggal_expired=%s,
            tanggal_edit=NOW(), updated_at=NOW()
        WHERE id=%s AND user_email=%s
    """

    cursor.execute(query, (nama_makanan, jumlah, tanggal_expired, food_id, current_user))
    connection.commit()

    cursor.close()
    connection.close()

    print("🟢 Food updated:", food_id)
    return "success"


@eel.expose
def delete_food(food_id):
    global current_user
    if not current_user:
        return "not_logged_in"

    connection = create_connection()
    if connection is None:
        return "db_error"

    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM foods WHERE id=%s AND user_email=%s",
        (food_id, current_user)
    )
    connection.commit()

    cursor.close()
    connection.close()

    print("🗑 Food deleted:", food_id)
    return "success"


# ====================================
# PASSWORD MANAGEMENT
# ====================================
@eel.expose
def update_password(current_password, new_password):
    global current_user
    if not current_user:
        return "not_logged_in"

    connection = create_connection()
    if connection is None:
        return "db_error"

    cursor = connection.cursor()
    cursor.execute("SELECT password FROM users WHERE email=%s", (current_user,))
    user = cursor.fetchone()

    if not user:
        return "user_not_found"

    hashed_current = hashlib.sha256(current_password.encode()).hexdigest()

    if hashed_current != user["password"]:
        return "wrong_password"

    hashed_new = hashlib.sha256(new_password.encode()).hexdigest()
    cursor.execute("UPDATE users SET password=%s WHERE email=%s", (hashed_new, current_user))
    connection.commit()

    cursor.close()
    connection.close()

    return "success"


@eel.expose
def delete_account(password):
    global current_user
    if not current_user:
        return "not_logged_in"

    connection = create_connection()
    if connection is None:
        return "db_error"

    cursor = connection.cursor()
    cursor.execute("SELECT password FROM users WHERE email=%s", (current_user,))
    user = cursor.fetchone()

    if not user:
        return "user_not_found"

    hashed_pw = hashlib.sha256(password.encode()).hexdigest()

    if hashed_pw != user["password"]:
        return "wrong_password"

    cursor.execute("DELETE FROM foods WHERE user_email=%s", (current_user,))
    cursor.execute("DELETE FROM users WHERE email=%s", (current_user,))

    connection.commit()
    cursor.close()
    connection.close()

    current_user = None
    return "success"


@eel.expose
def reset_password(email, new_password):
    connection = create_connection()
    if connection is None:
        return "db_error"

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if not user:
        return "not_found"

    hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()
    cursor.execute("UPDATE users SET password=%s WHERE email=%s", (hashed_pw, email))
    connection.commit()

    cursor.close()
    connection.close()

    return "success"


@eel.expose
def logout():
    global current_user
    current_user = None
    print("🔒 User logged out.")
    return "success"


# ====================================
# DATETIME FORMAT HELPERS
# ====================================
@eel.expose
def format_datetime(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S") if dt else None


@eel.expose
def format_date(d):
    return d.strftime("%Y-%m-%dT00:00:00") if d else None


# ====================================
# START APP (Chrome fallback)
# ====================================
if __name__ == "__main__":
    print("🚀 App running...")

    try:
        eel.start("register.html", mode="chrome", cmdline_args=["--start-fullscreen"], port=8001)
    except:
        print("⚠ Chrome not found. Opening in default window...")
        eel.start("register.html", size=(1200, 800), port=8001)
