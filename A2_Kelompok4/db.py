import sqlite3

def get_db_connection():
    """
    Mengembalikan objek koneksi SQLite dan mengaktifkan row_factory 
    agar hasil kueri bisa diakses seperti dictionary.
    """
    try:
        # Menghubungkan ke file database lokal 'recipe_id.db'
        conn = sqlite3.connect('recipe_id.db') 
        
        # Mengatur row_factory agar hasil bisa diakses dengan nama kolom (seperti dictionary)
        conn.row_factory = sqlite3.Row 
        return conn
    except sqlite3.Error as err:
        print(f"Error Koneksi Database SQLite: {err}")
        return None