import mysql.connector

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",      # Sesuaikan user MySQL
            password="",      # Sesuaikan password MySQL
            database="recipe_id"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error Koneksi Database: {err}")
        return None