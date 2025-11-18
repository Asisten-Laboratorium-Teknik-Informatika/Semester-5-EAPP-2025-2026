import eel
import hashlib
from db import get_connection

eel.init('web')

# Register
@eel.expose
def register_user(fullname, email, phone, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        hashed = hashlib.sha256(password.encode()).hexdigest()

        sql = "INSERT INTO users (fullname, email, phone, password) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (fullname, email, phone, hashed))

        conn.commit()
        return "success"

    except Exception as e:
        print(e)
        return "error"

# Login
@eel.expose
def login_user(email, password):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        hashed = hashlib.sha256(password.encode()).hexdigest()
        sql = "SELECT * FROM users WHERE email = %s AND password = %s"
        cursor.execute(sql, (email, hashed))

        user = cursor.fetchone()

        if user:
            return {
                "status": "success",
                "fullname": user["fullname"],
                "email": user["email"]
            }
        else:
            return { "status": "invalid" }

    except Exception as e:
        print(e)
        return { "status": "error" }



eel.start(
    'index.html',
    cmdline_args=['--start-maximized']
)
