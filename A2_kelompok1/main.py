import eel
from db import (
    init_db, 
    insert_kendaraan_masuk,
    get_kendaraan_parkir,
    update_kendaraan_keluar,
    get_riwayat_by_date,
    get_riwayat_by_range,  # FUNGSI BARU
    get_riwayat_parkir,
    get_statistics,
    register_user,
    login_user,
    get_user_by_id,
    get_statistik_per_hari,
    get_statistik_per_jenis,
    get_statistik_per_jam,
    get_statistik_per_hari_dalam_minggu
)

# Inisialisasi folder web
eel.init('web')

# ============================
#   FUNGSI UNTUK EEL (API)
# ============================

@eel.expose
def kendaraan_masuk(plat, jenis):
    """Handler kendaraan masuk"""
    print(f"📥 Kendaraan masuk: {plat} ({jenis})")
    result = insert_kendaraan_masuk(plat, jenis)
    print(f"📥 Result: {result}")
    return result

@eel.expose
def get_kendaraan_parkir_data():
    """Ambil daftar kendaraan yg sedang parkir"""
    result = get_kendaraan_parkir()
    print(f"📋 get_kendaraan_parkir_data: {len(result)} vehicles")
    return result

@eel.expose
def kendaraan_keluar(id):
    """Proses kendaraan keluar"""
    return update_kendaraan_keluar(id)

@eel.expose
def get_riwayat(selected_date=None):
    """
    Ambil riwayat berdasarkan tanggal atau semua riwayat.
    
    Args:
        selected_date (str, optional): Format YYYY-MM-DD
    
    Returns:
        list: Daftar riwayat parkir
    """
    if selected_date:
        result = get_riwayat_by_date(selected_date, selected_date)
        print(f"📋 get_riwayat (date={selected_date}): {len(result)} records")
        return result
    result = get_riwayat_parkir()
    print(f"📋 get_riwayat (all): {len(result)} records")
    return result

@eel.expose
def get_riwayat_by_time_range(range_type):
    """
    Ambil riwayat berdasarkan range waktu.
    
    Args:
        range_type (str): 'today', 'yesterday', 'week', 'month', 'year'
    
    Returns:
        list: Daftar riwayat parkir
    """
    return get_riwayat_by_range(range_type)

@eel.expose
def get_stats():
    """Ambil statistik untuk dashboard"""
    return get_statistics()

@eel.expose
def register(username, email, password, nama_lengkap):
    """Register user baru"""
    return register_user(username, email, password, nama_lengkap)

@eel.expose
def login(username, password):
    """Login user"""
    return login_user(username, password)

@eel.expose
def get_user(user_id):
    """Ambil data user berdasarkan ID"""
    return get_user_by_id(user_id)

@eel.expose
def get_chart_data_per_hari(days=7):
    """Ambil data statistik per hari untuk chart"""
    return get_statistik_per_hari(days)

@eel.expose
def get_chart_data_per_jenis():
    """Ambil data statistik per jenis kendaraan untuk chart"""
    return get_statistik_per_jenis()

@eel.expose
def get_chart_data_per_jam():
    """Ambil data statistik per jam untuk chart"""
    return get_statistik_per_jam()

@eel.expose
def get_chart_data_per_hari_minggu():
    """Ambil data statistik per hari dalam minggu untuk chart"""
    return get_statistik_per_hari_dalam_minggu()

# ============================
#        MAIN PROGRAM
# ============================

if __name__ == '__main__':
    print("=" * 50)
    print("🅿️  SISTEM PARKIR - Starting...")
    print("=" * 50)
    
    # Inisialisasi database
    init_db()
    
    print("✓ Database ready!")
    print("✓ Server ready!")
    print("✓ Opening UI...")
    print("=" * 50)
    
    # Start dengan login page
    eel.start('login.html', size=(1200, 800), port=8081)