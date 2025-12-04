import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from config import DB_CONFIG

# Inisialisasi database
def init_db():
    """Membuat database dan tabel jika belum ada"""
    try:
        # Koneksi tanpa database untuk membuat database jika belum ada
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Buat database jika belum ada
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"✓ Database '{DB_CONFIG['database']}' ready")
        
        cursor.close()
        conn.close()
        
        # Koneksi dengan database untuk membuat tabel
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kendaraan (
                id INT AUTO_INCREMENT PRIMARY KEY,
                plat VARCHAR(20) NOT NULL,
                jenis VARCHAR(20) NOT NULL,
                time_in DATETIME NOT NULL,
                time_out DATETIME NULL,
                durasi_menit INT NULL,
                biaya INT NULL,
                status VARCHAR(20) DEFAULT 'parkir',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Buat tabel users untuk authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                nama_lengkap VARCHAR(100) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        
        # Buat index untuk performa
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plat ON kendaraan(plat)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON kendaraan(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_time_in ON kendaraan(time_in)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON users(email)')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✓ Database initialized successfully")
    except Error as e:
        print(f"❌ Error initializing database: {e}")

# Fungsi untuk mendapatkan koneksi database
def get_db():
    """Mendapatkan koneksi database MySQL"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"❌ Error connecting to database: {e}")
        raise

# Helper function untuk convert row ke dict
def row_to_dict(cursor, row):
    """Convert MySQL row ke dictionary"""
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))

# Fungsi insert kendaraan masuk
def insert_kendaraan_masuk(plat, jenis):
    """
    Memasukkan data kendaraan yang baru masuk
    
    Args:
        plat (str): Nomor plat kendaraan
        jenis (str): Jenis kendaraan
    
    Returns:
        dict: {'success': bool, 'message': str, 'id': int}
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        time_in = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO kendaraan (plat, jenis, time_in, status)
            VALUES (%s, %s, %s, 'parkir')
        ''', (plat.upper(), jenis, time_in))
        
        kendaraan_id = cursor.lastrowid
        conn.commit()
        
        # Verifikasi data tersimpan
        cursor.execute('SELECT * FROM kendaraan WHERE id = %s', (kendaraan_id,))
        verify_row = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not verify_row:
            return {'success': False, 'message': 'Data gagal tersimpan ke database'}
        
        return {
            'success': True, 
            'message': f'Kendaraan {plat} berhasil masuk',
            'id': kendaraan_id
        }
    except Error as e:
        print(f"Error insert_kendaraan_masuk: {e}")
        return {'success': False, 'message': str(e)}

# Fungsi get kendaraan yang sedang parkir
def get_kendaraan_parkir():
    """
    Mengambil semua kendaraan yang sedang parkir
    
    Returns:
        list: List of dict kendaraan yang sedang parkir
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, plat, jenis, time_in
            FROM kendaraan
            WHERE status = 'parkir'
            ORDER BY time_in DESC
        ''')
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        result = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            result.append({
                'id': row_dict['id'],
                'plat': row_dict['plat'],
                'jenis': row_dict['jenis'],
                'time_in': str(row_dict['time_in']) if row_dict['time_in'] else None
            })
        
        cursor.close()
        conn.close()
        
        print(f"✓ get_kendaraan_parkir: Found {len(result)} vehicles")
        return result
    except Error as e:
        print(f"Error get_kendaraan_parkir: {e}")
        return []

# Fungsi update kendaraan keluar - DIPERBAIKI
def update_kendaraan_keluar(id):
    """
    Update kendaraan yang keluar, hitung durasi dan biaya
    
    Args:
        id (int): ID kendaraan
    
    Returns:
        dict: {'success': bool, 'message': str, 'durasi': int, 'biaya': int, 'jam': int}
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Ambil data kendaraan
        cursor.execute('SELECT * FROM kendaraan WHERE id = %s', (id,))
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            conn.close()
            return {'success': False, 'message': 'Kendaraan tidak ditemukan'}
        
        # Convert row ke dict
        columns = [desc[0] for desc in cursor.description]
        row_dict = dict(zip(columns, row))
        
        # Hitung durasi
        time_in = row_dict['time_in']
        if isinstance(time_in, str):
            time_in = datetime.strptime(time_in, '%Y-%m-%d %H:%M:%S')
        elif isinstance(time_in, datetime):
            pass
        else:
            time_in = datetime.strptime(str(time_in), '%Y-%m-%d %H:%M:%S')
        
        time_out = datetime.now()
        
        durasi_menit = int((time_out - time_in).total_seconds() / 60)
        if durasi_menit < 1:
            durasi_menit = 1  # Minimal 1 menit
        
        # Tarif parkir berdasarkan jenis kendaraan
        tarif = {
            'Motor': 2000,
            'Mobil': 5000,
            'Truk': 10000,
            'Bus': 15000,
            'Sepeda': 1000,
            'Pickup': 7000
        }
        
        biaya_per_jam = tarif.get(row_dict['jenis'], 5000)
        
        # PERBAIKAN: Hitung jam dengan pembulatan ke atas
        # Jika durasi < 60 menit, tetap dihitung 1 jam
        # Jika durasi >= 60 menit, pembulatan ke atas
        import math
        jam = math.ceil(durasi_menit / 60)
        
        # Hitung biaya total
        biaya = jam * biaya_per_jam
        
        # Update database
        cursor.execute('''
            UPDATE kendaraan
            SET time_out = %s, durasi_menit = %s, biaya = %s, status = 'selesai'
            WHERE id = %s
        ''', (time_out.strftime('%Y-%m-%d %H:%M:%S'), durasi_menit, biaya, id))
        
        conn.commit()
        
        # Verifikasi update
        cursor.execute('SELECT * FROM kendaraan WHERE id = %s', (id,))
        verify_row = cursor.fetchone()
        
        if verify_row:
            verify_columns = [desc[0] for desc in cursor.description]
            verify_dict = dict(zip(verify_columns, verify_row))
            if verify_dict['status'] != 'selesai':
                cursor.close()
                conn.close()
                return {'success': False, 'message': 'Update status gagal'}
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'message': 'Kendaraan berhasil keluar',
            'durasi': durasi_menit,
            'biaya': biaya,
            'jam': jam
        }
    except Error as e:
        print(f"Error update_kendaraan_keluar: {e}")
        return {'success': False, 'message': str(e)}

# Fungsi get riwayat parkir
def get_riwayat_parkir(limit=100):
    """
    Mengambil riwayat parkir yang sudah selesai
    
    Args:
        limit (int): Jumlah data maksimal yang diambil
    
    Returns:
        list: List of dict riwayat parkir
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, plat, jenis, time_in, time_out, durasi_menit, biaya
            FROM kendaraan
            WHERE status = 'selesai'
            ORDER BY time_out DESC
            LIMIT %s
        ''', (limit,))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        result = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            result.append({
                'id': row_dict['id'],
                'plat': row_dict['plat'],
                'jenis': row_dict['jenis'],
                'time_in': str(row_dict['time_in']) if row_dict['time_in'] else None,
                'time_out': str(row_dict['time_out']) if row_dict['time_out'] else None,
                'durasi_menit': row_dict['durasi_menit'],
                'biaya': row_dict['biaya']
            })
        
        cursor.close()
        conn.close()
        
        print(f"✓ get_riwayat_parkir: Found {len(result)} records")
        return result
    except Error as e:
        print(f"Error get_riwayat_parkir: {e}")
        return []

# Fungsi get riwayat berdasarkan tanggal
def get_riwayat_by_date(start_date, end_date):
    """
    Mengambil riwayat parkir berdasarkan range tanggal
    
    Args:
        start_date (str): Tanggal mulai (YYYY-MM-DD)
        end_date (str): Tanggal akhir (YYYY-MM-DD)
    
    Returns:
        list: List of dict riwayat parkir
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, plat, jenis, time_in, time_out, durasi_menit, biaya
            FROM kendaraan
            WHERE status = 'selesai'
            AND DATE(time_out) BETWEEN %s AND %s
            ORDER BY time_out DESC
        ''', (start_date, end_date))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        result = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            result.append({
                'id': row_dict['id'],
                'plat': row_dict['plat'],
                'jenis': row_dict['jenis'],
                'time_in': str(row_dict['time_in']) if row_dict['time_in'] else None,
                'time_out': str(row_dict['time_out']) if row_dict['time_out'] else None,
                'durasi_menit': row_dict['durasi_menit'],
                'biaya': row_dict['biaya']
            })
        
        cursor.close()
        conn.close()
        
        return result
    except Error as e:
        print(f"Error get_riwayat_by_date: {e}")
        return []

# FUNGSI BARU: Get riwayat berdasarkan range waktu
def get_riwayat_by_range(range_type):
    """
    Mengambil riwayat berdasarkan range waktu
    
    Args:
        range_type (str): 'today', 'yesterday', 'week', 'month'
    
    Returns:
        list: List of dict riwayat parkir
    """
    today = datetime.now().date()
    
    if range_type == 'today':
        start_date = today
        end_date = today
    elif range_type == 'yesterday':
        start_date = today - timedelta(days=1)
        end_date = today - timedelta(days=1)
    elif range_type == 'week':
        # Minggu ini (Senin - Minggu)
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif range_type == 'month':
        # Bulan ini
        start_date = today.replace(day=1)
        end_date = today
    elif range_type == 'year':
        # Tahun ini
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        # Default: hari ini
        start_date = today
        end_date = today
    
    return get_riwayat_by_date(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )

# Fungsi get statistik
def get_statistics():
    """
    Mengambil statistik parkir
    
    Returns:
        dict: {'total_parkir': int, 'transaksi_hari_ini': int, 'pendapatan_hari_ini': int}
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Total kendaraan parkir
        cursor.execute("SELECT COUNT(*) as count FROM kendaraan WHERE status = 'parkir'")
        total_parkir = cursor.fetchone()[0]
        
        # Transaksi hari ini
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute(
            "SELECT COUNT(*) as count FROM kendaraan WHERE status = 'selesai' AND DATE(time_out) = %s",
            (today,)
        )
        transaksi_hari_ini = cursor.fetchone()[0]
        
        # Pendapatan hari ini
        cursor.execute(
            "SELECT COALESCE(SUM(biaya), 0) as total FROM kendaraan WHERE status = 'selesai' AND DATE(time_out) = %s",
            (today,)
        )
        pendapatan_hari_ini = cursor.fetchone()[0] or 0
        
        cursor.close()
        conn.close()
        
        return {
            'total_parkir': total_parkir,
            'transaksi_hari_ini': transaksi_hari_ini,
            'pendapatan_hari_ini': int(pendapatan_hari_ini)
        }
    except Error as e:
        print(f"Error get_statistics: {e}")
        return {
            'total_parkir': 0,
            'transaksi_hari_ini': 0,
            'pendapatan_hari_ini': 0
        }

# ============================
#   FUNGSI STATISTIK UNTUK VISUALISASI
# ============================

def get_statistik_per_hari(days=7):
    """
    Mengambil statistik transaksi per hari untuk beberapa hari terakhir
    
    Args:
        days (int): Jumlah hari terakhir (default: 7)
    
    Returns:
        list: List of dict dengan format [{'tanggal': 'YYYY-MM-DD', 'transaksi': int, 'pendapatan': int}, ...]
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Query untuk mendapatkan statistik per hari
        cursor.execute('''
            SELECT 
                DATE(time_out) as tanggal,
                COUNT(*) as transaksi,
                COALESCE(SUM(biaya), 0) as pendapatan
            FROM kendaraan
            WHERE status = 'selesai' 
                AND time_out IS NOT NULL
                AND DATE(time_out) >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY DATE(time_out)
            ORDER BY tanggal ASC
        ''', (days,))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        result = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            result.append({
                'tanggal': str(row_dict['tanggal']),
                'transaksi': int(row_dict['transaksi']),
                'pendapatan': int(row_dict['pendapatan']) if row_dict['pendapatan'] else 0
            })
        
        cursor.close()
        conn.close()
        
        return result
    except Error as e:
        print(f"Error get_statistik_per_hari: {e}")
        return []

def get_statistik_per_jenis():
    """
    Mengambil statistik transaksi per jenis kendaraan
    
    Returns:
        list: List of dict dengan format [{'jenis': str, 'jumlah': int, 'pendapatan': int}, ...]
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                jenis,
                COUNT(*) as jumlah,
                COALESCE(SUM(biaya), 0) as pendapatan
            FROM kendaraan
            WHERE status = 'selesai'
            GROUP BY jenis
            ORDER BY jumlah DESC
        ''')
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        result = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            result.append({
                'jenis': row_dict['jenis'],
                'jumlah': int(row_dict['jumlah']),
                'pendapatan': int(row_dict['pendapatan']) if row_dict['pendapatan'] else 0
            })
        
        cursor.close()
        conn.close()
        
        return result
    except Error as e:
        print(f"Error get_statistik_per_jenis: {e}")
        return []

def get_statistik_per_jam():
    """
    Mengambil statistik transaksi per jam (untuk melihat jam-jam ramai)
    
    Returns:
        list: List of dict dengan format [{'jam': int, 'transaksi': int}, ...]
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                HOUR(time_out) as jam,
                COUNT(*) as transaksi
            FROM kendaraan
            WHERE status = 'selesai' 
                AND time_out IS NOT NULL
                AND DATE(time_out) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY HOUR(time_out)
            ORDER BY jam ASC
        ''')
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        result = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            result.append({
                'jam': int(row_dict['jam']),
                'transaksi': int(row_dict['transaksi'])
            })
        
        cursor.close()
        conn.close()
        
        return result
    except Error as e:
        print(f"Error get_statistik_per_jam: {e}")
        return []

def get_statistik_per_hari_dalam_minggu():
    """
    Mengambil statistik transaksi per hari dalam minggu (Senin-Minggu)
    
    Returns:
        list: List of dict dengan format [{'hari': str, 'transaksi': int, 'pendapatan': int}, ...]
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                DAYNAME(time_out) as hari,
                DAYOFWEEK(time_out) as hari_num,
                COUNT(*) as transaksi,
                COALESCE(SUM(biaya), 0) as pendapatan
            FROM kendaraan
            WHERE status = 'selesai' 
                AND time_out IS NOT NULL
                AND DATE(time_out) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY DAYNAME(time_out), DAYOFWEEK(time_out)
            ORDER BY hari_num ASC
        ''')
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # Mapping hari dalam bahasa Indonesia dan urutan
        hari_map = {
            'Monday': {'nama': 'Senin', 'urutan': 1},
            'Tuesday': {'nama': 'Selasa', 'urutan': 2},
            'Wednesday': {'nama': 'Rabu', 'urutan': 3},
            'Thursday': {'nama': 'Kamis', 'urutan': 4},
            'Friday': {'nama': 'Jumat', 'urutan': 5},
            'Saturday': {'nama': 'Sabtu', 'urutan': 6},
            'Sunday': {'nama': 'Minggu', 'urutan': 7}
        }
        
        result = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            hari_en = row_dict['hari']
            hari_info = hari_map.get(hari_en, {'nama': hari_en, 'urutan': 0})
            result.append({
                'hari': hari_info['nama'],
                'urutan': hari_info['urutan'],
                'transaksi': int(row_dict['transaksi']),
                'pendapatan': int(row_dict['pendapatan']) if row_dict['pendapatan'] else 0
            })
        
        # Sort by urutan (Senin-Minggu)
        result.sort(key=lambda x: x['urutan'])
        
        cursor.close()
        conn.close()
        
        return result
    except Error as e:
        print(f"Error get_statistik_per_hari_dalam_minggu: {e}")
        return []

# ============================
#   FUNGSI AUTHENTICATION
# ============================

import hashlib

def hash_password(password):
    """Hash password menggunakan SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password, nama_lengkap):
    """
    Register user baru
    
    Args:
        username (str): Username
        email (str): Email
        password (str): Password (akan di-hash)
        nama_lengkap (str): Nama lengkap
    
    Returns:
        dict: {'success': bool, 'message': str, 'user_id': int}
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Cek apakah username sudah ada
        cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {'success': False, 'message': 'Username sudah digunakan'}
        
        # Cek apakah email sudah ada
        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {'success': False, 'message': 'Email sudah digunakan'}
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Insert user baru
        cursor.execute('''
            INSERT INTO users (username, email, password, nama_lengkap, role)
            VALUES (%s, %s, %s, %s, 'user')
        ''', (username, email, hashed_password, nama_lengkap))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'message': 'Registrasi berhasil! Silakan login.',
            'user_id': user_id
        }
    except Error as e:
        print(f"Error register_user: {e}")
        return {'success': False, 'message': f'Terjadi kesalahan: {str(e)}'}

def login_user(username, password):
    """
    Login user
    
    Args:
        username (str): Username atau email
        password (str): Password
    
    Returns:
        dict: {'success': bool, 'message': str, 'user': dict}
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Hash password untuk dicocokkan
        hashed_password = hash_password(password)
        
        # Cek apakah login dengan username atau email
        cursor.execute('''
            SELECT id, username, email, nama_lengkap, role
            FROM users
            WHERE (username = %s OR email = %s) AND password = %s
        ''', (username, username, hashed_password))
        
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            conn.close()
            return {'success': False, 'message': 'Username/email atau password salah'}
        
        # Convert row ke dict
        columns = [desc[0] for desc in cursor.description]
        user_dict = dict(zip(columns, row))
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'message': 'Login berhasil!',
            'user': {
                'id': user_dict['id'],
                'username': user_dict['username'],
                'email': user_dict['email'],
                'nama_lengkap': user_dict['nama_lengkap'],
                'role': user_dict['role']
            }
        }
    except Error as e:
        print(f"Error login_user: {e}")
        return {'success': False, 'message': f'Terjadi kesalahan: {str(e)}'}

def get_user_by_id(user_id):
    """
    Ambil data user berdasarkan ID
    
    Args:
        user_id (int): User ID
    
    Returns:
        dict: Data user atau None
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, nama_lengkap, role, created_at
            FROM users
            WHERE id = %s
        ''', (user_id,))
        
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            conn.close()
            return None
        
        columns = [desc[0] for desc in cursor.description]
        user_dict = dict(zip(columns, row))
        
        cursor.close()
        conn.close()
        
        return user_dict
    except Error as e:
        print(f"Error get_user_by_id: {e}")
        return None
