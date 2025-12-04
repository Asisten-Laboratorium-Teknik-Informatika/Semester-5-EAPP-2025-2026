# db.py
import mysql.connector
from argon2 import PasswordHasher

ph = PasswordHasher()

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="kilas_db"
    )

def register_user_in_db(username, email, password):
    conn = get_db()
    cursor = conn.cursor()
    try:
        hashed = ph.hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed)
        )
        conn.commit()
        return True, "Pendaftaran berhasil"
    except mysql.connector.Error as err:
        return False, f"{err}"
    finally:
        cursor.close()
        conn.close()

def login_user_in_db(email, password):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username, email, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            return False, None, "Email atau password salah"

        username, email_db, hashed_password = user
        try:
            ph.verify(hashed_password, password)
            return True, {"username": username, "email": email_db}, "Login berhasil"
        except:
            return False, None, "Email atau password salah"
    except mysql.connector.Error as err:
        return False, None, f"{err}"
    finally:
        cursor.close()
        conn.close()
