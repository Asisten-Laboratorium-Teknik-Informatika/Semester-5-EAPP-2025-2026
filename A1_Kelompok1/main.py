import sys, os
import eel
import mysql.connector
from mysql.connector import Error


# ============================
#   FIX PATH (SUPPORT EXE)
# ============================
def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.abspath("."), relative)

web_folder = resource_path("web")
eel.init(web_folder)


# ============================
#  DATABASE CONNECTION
# ============================
def connect_db():
    try:
        db = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="nutriplan",
            port=3306   
        )
        print("DB Connected!")
        return db

    except Error as e:
        print("DB ERROR:", e) 
        return None


# ============================
#  LOGIN FUNCTION
# ============================
@eel.expose
def login(email, password):
    print("Login Attempt ->", email, password)

    if email == "" or password == "":
        return {"status": "empty"}

    db = connect_db()
    if db is None:
        return {"status": "dberror"}

    cursor = db.cursor()

    sql = "SELECT id, email, password FROM users WHERE email = %s AND password = %s"
    val = (email, password)
    cursor.execute(sql, val)

    user = cursor.fetchone()
    db.close()

    if user:
        return {
            "status": "success",
            "user_id": user[0],
            "email": user[1]
        }
    else:
        return {"status": "invalid"}


# ============================
#  REGISTER FUNCTION
# ============================
@eel.expose
def register(name, email, password):
    print("Register Attempt ->", name, email, password)

    if name == "" or email == "" or password == "":
        return "empty"

    db = connect_db()
    if db is None:
        return "dberror"

    cursor = db.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    existing = cursor.fetchone()

    if existing:
        db.close()
        return "exists"

    sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
    val = (name, email, password)
    cursor.execute(sql, val)
    db.commit()
    db.close()

    return "success"


# ============================
#  SAVE FOOD LOG
# ============================
@eel.expose
def save_food_log(user_id, kategori, nama, qty, unit, kalori_total):
    db = connect_db()
    if db is None:
        return "dberror"

    cur = db.cursor()

    sql = """
        INSERT INTO food_log (user_id, kategori, nama, qty, unit, kalori)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    val = (user_id, kategori, nama, qty, unit, kalori_total)

    cur.execute(sql, val)
    db.commit()
    db.close()

    return "saved"


# ============================
#  GET FOOD DATABASE
# ============================
@eel.expose
def get_all_food():
    db = connect_db()
    if db is None:
        return []

    cur = db.cursor()
    cur.execute("SELECT nama, kalori_per100 FROM food_database")
    data = cur.fetchall()
    db.close()

    return data


# ============================
#  GET FOOD HISTORY
# ============================
@eel.expose
def get_food_history(user_id):
    db = connect_db()
    if db is None:
        return []

    cur = db.cursor()
    sql = """
        SELECT id, kategori, nama, qty, unit, kalori, tanggal
        FROM food_log
        WHERE user_id = %s
        ORDER BY tanggal DESC, id DESC
    """
    cur.execute(sql, (user_id,))
    rows = cur.fetchall()
    db.close()

    hasil = []
    for r in rows:
        hasil.append({
            "id": r[0],
            "kategori": r[1],
            "nama": r[2],
            "qty": r[3],
            "unit": r[4],
            "kalori": r[5],
            "tanggal": r[6].strftime("%Y-%m-%d") if r[6] else None
        })

    return hasil


# ============================
#  BMI CATEGORY
# ============================
def kategori_bmi(bmi):
    if bmi < 18.5:
        return "Kurus"
    elif 18.5 <= bmi < 23:
        return "Normal"
    elif 23 <= bmi < 27.5:
        return "Overweight"
    else:
        return "Obesitas"


# ============================
#  SAVE BMI HISTORY
# ============================
@eel.expose
def save_bmi(user_id, berat, tinggi):
    try:
        berat = float(berat)
        tinggi = float(tinggi)
    except ValueError:
        return {"status": "invalid_input"}

    if tinggi <= 0 or berat <= 0:
        return {"status": "invalid_input"}

    tinggi_meter = tinggi / 100.0
    bmi = berat / (tinggi_meter ** 2)
    status = kategori_bmi(bmi)

    db = connect_db()
    if db is None:
        return {"status": "dberror"}

    cur = db.cursor()

    sql = """
        INSERT INTO bmi_history (user_id, berat, tinggi, bmi, status)
        VALUES (%s, %s, %s, %s, %s)
    """
    val = (user_id, berat, tinggi, bmi, status)

    cur.execute(sql, val)
    db.commit()
    db.close()

    return {
        "status": "bmi_saved",
        "bmi": round(bmi, 2),
        "kategori": status
    }


# ============================
#  START APP
# ============================
if __name__ == "__main__":
   eel.start("signin.html", size=(1440, 1024), port=8890, block=True)

