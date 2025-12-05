# main.py
import eel
import sqlite3
import os
from datetime import datetime

WEB_DIR = "web"
DB_PATH = "donasi.db"

# --- DEBUG: CEK STRUKTUR FOLDER ---
print("=" * 50)
print("DEBUG: Checking folder structure...")
print("Current working directory:", os.getcwd())
print("Web directory exists:", os.path.exists(WEB_DIR))

if os.path.exists(WEB_DIR):
    print("Files in web directory:")
    for file in os.listdir(WEB_DIR):
        print(f"  - {file}")
    
    css_path = os.path.join(WEB_DIR, "css")
    if os.path.exists(css_path):
        print("CSS folder exists, files in css:")
        for css_file in os.listdir(css_path):
            print(f"    - {css_file}")
    else:
        print("WARNING: CSS folder not found in web directory!")
else:
    print("ERROR: Web directory not found!")
    print("Please ensure the folder structure is:")
    print("project/")
    print("├── web/     (folder with HTML/CSS/JS files)")
    print("└── main.py  (this file)")
    input("Press Enter to exit...")
    exit(1)
print("=" * 50)

eel.init(WEB_DIR)
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()

# --- DATABASE SETUP ---
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'operator'
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS donatur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    contact TEXT,
    created_at TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS panti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    alamat TEXT,
    kontak TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS penerima (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    kebutuhan TEXT,
    panti_id INTEGER,
    created_at TEXT,
    FOREIGN KEY(panti_id) REFERENCES panti(id)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS donasi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donatur_id INTEGER NOT NULL,
    penerima_id INTEGER NOT NULL,
    jumlah REAL NOT NULL,
    keterangan TEXT,
    created_at TEXT,
    FOREIGN KEY(donatur_id) REFERENCES donatur(id),
    FOREIGN KEY(penerima_id) REFERENCES penerima(id)
)
''')

conn.commit()

# --- DEFAULT ADMIN ---
def ensure_default_admin():
    c.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ("admin", "admin123", "admin"))
        conn.commit()
        print("Default admin created: admin / admin123")

ensure_default_admin()

# === API (Eel exposed) ===

@eel.expose
def api_login(username, password):
    c.execute("SELECT id, username, role FROM users WHERE username=? AND password=?", (username, password))
    row = c.fetchone()
    if row:
        uid, uname, role = row
        return {"ok": True, "user": {"id": uid, "username": uname, "role": role}}
    else:
        return {"ok": False, "message": "Login gagal"}

# Donatur
@eel.expose
def api_add_donatur(nama, contact):
    now = datetime.utcnow().isoformat()
    c.execute("INSERT INTO donatur (nama, contact, created_at) VALUES (?, ?, ?)", (nama, contact, now))
    conn.commit()
    return {"ok": True, "donatur_id": c.lastrowid}

# Panti
@eel.expose
def api_add_panti(nama, alamat="", kontak=""):
    if not nama:
        return {"ok": False, "message": "Nama panti wajib"}
    alamat_val = alamat or ""
    kontak_val = kontak or ""
    c.execute("INSERT INTO panti (nama, alamat, kontak) VALUES (?, ?, ?)", (nama, alamat_val, kontak_val))
    conn.commit()
    return {"ok": True, "panti_id": c.lastrowid}

@eel.expose
def api_get_all_panti():
    c.execute("SELECT id, nama, alamat, kontak FROM panti ORDER BY id DESC")
    rows = c.fetchall()
    return [{"id": r[0], "nama": r[1], "alamat": r[2], "kontak": r[3]} for r in rows]

# Penerima (add + optionally record donation)
@eel.expose
def api_add_penerima(nama, kebutuhan, panti_id=None):
    now = datetime.utcnow().isoformat()
    if not nama:
        return {"ok": False, "message": "Nama penerima wajib"}
    c.execute("INSERT INTO penerima (nama, kebutuhan, panti_id, created_at) VALUES (?, ?, ?, ?)",
              (nama, kebutuhan, panti_id, now))
    conn.commit()
    return {"ok": True, "penerima_id": c.lastrowid}

@eel.expose
def api_get_all_penerima():
    c.execute("""
        SELECT p.id, p.nama, p.kebutuhan, p.panti_id, pa.nama
        FROM penerima p
        LEFT JOIN panti pa ON p.panti_id = pa.id
        ORDER BY p.id DESC
    """)
    rows = c.fetchall()
    return [{"id": r[0], "nama": r[1], "kebutuhan": r[2], "panti_id": r[3], "panti_nama": r[4]} for r in rows]

# Donasi
@eel.expose
def api_record_donation(donatur_id, penerima_id, jumlah, keterangan=""):
    now = datetime.utcnow().isoformat()
    try:
        jumlah_val = float(jumlah)
    except:
        jumlah_val = 0.0
    c.execute("INSERT INTO donasi (donatur_id, penerima_id, jumlah, keterangan, created_at) VALUES (?, ?, ?, ?, ?)",
              (donatur_id, penerima_id, jumlah_val, keterangan, now))
    conn.commit()
    return {"ok": True, "donation_id": c.lastrowid}

@eel.expose
def api_get_donations():
    c.execute("""
        SELECT dn.id, d.nama AS donatur, p.nama AS penerima, dn.jumlah, dn.created_at
        FROM donasi dn
        JOIN donatur d ON dn.donatur_id = d.id
        JOIN penerima p ON dn.penerima_id = p.id
        ORDER BY dn.id DESC
    """)
    rows = c.fetchall()
    return [(r[0], r[1], r[2], r[3], r[4]) for r in rows]

@eel.expose
def api_get_summary():
    c.execute("SELECT COALESCE(SUM(jumlah),0) FROM donasi")
    total = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM donatur")
    count_donors = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM penerima")
    count_recipients = c.fetchone()[0] or 0
    return {"total": total, "donors": count_donors, "recipients": count_recipients}

if __name__ == "__main__":
    print("Starting Eel application...")
    print("If you see any CSS errors above, please create the css folder structure.")
    eel.start("index.html", size=(1100, 700), block=True)