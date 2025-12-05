import eel
import json
import mysql.connector
from datetime import datetime, date

# inisialisasi folder web
eel.init('web')

# ----- Koneksi database -----
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bigfive_db"
    )

@eel.expose
def save_user(data):
    """Menyimpan data user + skor Big Five ke MySQL"""

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO users 
            (name, dob, age, gender, education, occupation, email, 
             O, C, E, A, N)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data.get("name"),
            data.get("dob"),
            data.get("age"),
            data.get("gender"),
            data.get("education"),
            data.get("occupation"),
            data.get("email"),
            data.get("O"),
            data.get("C"),
            data.get("E"),
            data.get("A"),
            data.get("N")
        )

        cursor.execute(sql, values)
        conn.commit()

        return "Data berhasil disimpan!"

    except Error as e:
        return f"ERROR: {e}"

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@eel.expose
def get_trait_analysis(trait, score):
    """Dapatkan analisis untuk trait tertentu"""
    analyses = {
        "O": {
            "high": "Anda memiliki pikiran yang sangat terbuka dan kreatif.",
            "medium": "Anda memiliki keseimbangan antara kreativitas dan kepraktisan.",
            "low": "Anda lebih praktis dan fokus pada hal-hal konkret."
        },
        "C": {
            "high": "Anda sangat terorganisir dan dapat diandalkan.",
            "medium": "Anda memiliki tingkat disiplin yang moderat.",
            "low": "Anda lebih fleksibel dan spontan."
        },
        "E": {
            "high": "Anda sangat energik dan menikmati interaksi sosial.",
            "medium": "Anda nyaman baik dalam situasi sosial maupun sendiri.",
            "low": "Anda lebih introvert dan menghargai waktu sendiri."
        },
        "A": {
            "high": "Anda sangat kooperatif dan peduli dengan orang lain.",
            "medium": "Anda memiliki keseimbangan antara kepedulian dan ketegasan.",
            "low": "Anda lebih kompetitif dan fokus pada tujuan pribadi."
        },
        "N": {
            "high": "Anda mungkin lebih sensitif terhadap stres.",
            "medium": "Anda memiliki stabilitas emosional yang moderat.",
            "low": "Anda sangat tenang dan stabil secara emosional."
        }
    }

    try:
        numeric_score = float(score)
    except Exception:
        numeric_score = 0

    level = "high" if numeric_score >= 70 else "medium" if numeric_score >= 40 else "low"
    return analyses.get(trait, {}).get(level, "")

# ----- Jalankan aplikasi -----
if __name__ == '__main__':
    print("\n" + "="*50)
    print("   BIG FIVE PERSONALITY TEST")
    print("="*50)
    print("\n[INFO] Memulai aplikasi...")
    print("[INFO] Membuka browser...\n")

    try:
        eel.start('index.html', size=(1200, 800), port=8080)
    except Exception:
        eel.start('index.html', size=(1200, 800), port=8000)
