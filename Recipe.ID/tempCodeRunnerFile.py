import eel
import db
import base64
import os
import time
import datetime

eel.init('web')

# --- HELPER ---
def proses_upload_gambar(nama_file, data_base64):
    if not data_base64 or not nama_file: return None
    try:
        folder_path = "web/assets/uploaded"
        if not os.path.exists(folder_path): os.makedirs(folder_path)
        if "," in data_base64: header, encoded = data_base64.split(",", 1)
        else: encoded = data_base64
        ext = nama_file.split('.')[-1]
        nama_unik = f"{int(time.time())}.{ext}"
        full_path = f"{folder_path}/{nama_unik}"
        with open(full_path, "wb") as fh: fh.write(base64.b64decode(encoded))
        return f"assets/uploaded/{nama_unik}"
    except Exception as e:
        print(f"Gagal upload: {e}")
        return None

# --- 1. DASHBOARD ---
@eel.expose
def ambil_data_dashboard():
    conn = db.get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as total FROM recipes")
        stats_resep = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM categories")
        stats_kat = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM recipes WHERE is_favorite = 1")
        stats_fav = cursor.fetchone()['total']

        cursor.execute("SELECT id, title, description, image_path FROM recipes ORDER BY RAND() LIMIT 3")
        rekomendasi = cursor.fetchall()

        cursor.execute("""
            SELECT r.id, r.title, r.image_path 
            FROM recipes r
            JOIN recipe_categories rc ON r.id = rc.recipe_id
            JOIN categories c ON rc.category_id = c.id
            WHERE c.name = 'Cemilan'
            ORDER BY RAND() LIMIT 5
        """)
        rek_cemilan = cursor.fetchall()

        cursor.execute("""
            SELECT r.id, r.title, r.image_path 
            FROM recipes r
            JOIN recipe_categories rc ON r.id = rc.recipe_id
            JOIN categories c ON rc.category_id = c.id
            WHERE c.name = 'Minuman'
            ORDER BY RAND() LIMIT 5
        """)
        rek_minuman = cursor.fetchall()

        cursor.execute("""
            SELECT r.id, r.title, r.image_path, r.created_at, 
            GROUP_CONCAT(c.name SEPARATOR ', ') as category_name
            FROM recipes r 
            LEFT JOIN recipe_categories rc ON r.id = rc.recipe_id
            LEFT JOIN categories c ON rc.category_id = c.id
            GROUP BY r.id
            ORDER BY r.created_at DESC LIMIT 5
        """)
        terbaru = cursor.fetchall()

        hari_eng = datetime.datetime.now().strftime("%A")
        map_hari = {'Monday':'Senin', 'Tuesday':'Selasa', 'Wednesday':'Rabu', 'Thursday':'Kamis', 'Friday':'Jumat', 'Saturday':'Sabtu', 'Sunday':'Minggu'}
        hari_ini = map_hari.get(hari_eng, 'Senin')

        cursor.execute("""
            SELECT mp.meal_type, r.id, r.title, r.image_path 
            FROM meal_plans mp
            JOIN recipes r ON mp.recipe_id = r.id
            WHERE mp.day_name = %s
        """, (hari_ini,))
        rencana_db = cursor.fetchall()

        rencana_struct = {'Sarapan': None, 'Siang': None, 'Malam': None}
        for r in rencana_db:
            rencana_struct[r['meal_type']] = r

        conn.close()
        
        return {
            "stats": {"resep": stats_resep, "kategori": stats_kat, "favorit": stats_fav},
            "rekomendasi": rekomendasi,
            "cemilan": rek_cemilan,
            "minuman": rek_minuman,
            "terbaru": terbaru,
            "rencana_hari_ini": {"hari": hari_ini, "menu": rencana_struct},
            "status": "Terkoneksi"
        }
    return {"status": "Error Database"}

# --- 2. KATEGORI ---
@eel.expose
def ambil_kategori():
    conn = db.get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories ORDER BY name ASC")
    res = cursor.fetchall()
    conn.close()
    return res

@eel.expose
def tambah_kategori_baru(nama):
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (name) VALUES (%s)", (nama,))
        conn.commit()
        return {"sukses": True, "pesan": "Kategori ditambah!"}
    except Exception as e: return {"sukses": False, "pesan": str(e)}
    finally: conn.close()

@eel.expose
def hapus_kategori(id_kat):
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id=%s", (id_kat,))
        conn.commit()
        return {"sukses": True, "pesan": "Kategori dihapus!"}
    except: return {"sukses": False, "pesan": "Gagal: Kategori sedang dipakai."}
    finally: conn.close()

# --- 3. CRUD RESEP ---
@eel.expose
def simpan_resep_baru(data):
    conn = db.get_db_connection()
    try:
        path_gambar = proses_upload_gambar(data.get('nama_file'), data.get('file_base64'))
        cursor = conn.cursor()
        query = "INSERT INTO recipes (title, description, servings, image_path) VALUES (%s, %s, %s, %s)"
        val = (data['judul'], data['deskripsi'], 1, path_gambar)
        cursor.execute(query, val)
        resep_id = cursor.lastrowid
        for kat_id in data['kategori_ids']:
            cursor.execute("INSERT INTO recipe_categories (recipe_id, category_id) VALUES (%s, %s)", (resep_id, kat_id))
        for b in data['bahan']:
            cursor.execute("INSERT INTO ingredients (recipe_id, item_name, quantity, unit) VALUES (%s, %s, %s, %s)", (resep_id, b['nama'], b['jumlah'], b['satuan']))
        for idx, step in enumerate(data['langkah']):
            cursor.execute("INSERT INTO steps (recipe_id, step_number, instruction) VALUES (%s, %s, %s)", (resep_id, idx+1, step))
        conn.commit()
        return {"sukses": True, "pesan": "Resep tersimpan!"}
    except Exception as e: return {"sukses": False, "pesan": str(e)}
    finally: conn.close()

# --- UPDATE DENGAN FITUR HAPUS GAMBAR LAMA ---
@eel.expose
def update_resep_lama(id_resep, data):
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True) # Pakai dictionary biar gampang ambil nama kolom
        
        # 1. Proses Gambar Baru
        path_gambar_baru = proses_upload_gambar(data.get('nama_file'), data.get('file_base64'))
        
        if path_gambar_baru:
            # === LOGIC PENGHAPUSAN FILE LAMA ===
            # Ambil path gambar lama dari database sebelum di-timpa
            cursor.execute("SELECT image_path FROM recipes WHERE id=%s", (id_resep,))
            hasil_lama = cursor.fetchone()
            
            if hasil_lama and hasil_lama['image_path']:
                path_lama = hasil_lama['image_path']
                # Path di DB: "assets/uploaded/..."
                # Kita perlu tambah "web/" di depannya karena script jalan dari root folder
                full_path_lama = os.path.join("web", path_lama)
                
                # Cek apakah file ada, lalu hapus
                if os.path.exists(full_path_lama):
                    try:
                        os.remove(full_path_lama)
                        print(f"Berhasil menghapus file lama: {full_path_lama}")
                    except Exception as e_del:
                        print(f"Gagal hapus file: {e_del}")
            # ===================================

            # Update Database dengan Gambar Baru
            query = "UPDATE recipes SET title=%s, description=%s, image_path=%s WHERE id=%s"
            val = (data['judul'], data['deskripsi'], path_gambar_baru, id_resep)
        else:
            # Tidak ada gambar baru, update teks saja
            query = "UPDATE recipes SET title=%s, description=%s WHERE id=%s"
            val = (data['judul'], data['deskripsi'], id_resep)
            
        cursor.execute(query, val)

        # Reset Kategori, Bahan, Langkah (Sama seperti sebelumnya)
        cursor.execute("DELETE FROM recipe_categories WHERE recipe_id=%s", (id_resep,))
        for kat_id in data['kategori_ids']:
            cursor.execute("INSERT INTO recipe_categories (recipe_id, category_id) VALUES (%s, %s)", (id_resep, kat_id))
        cursor.execute("DELETE FROM ingredients WHERE recipe_id=%s", (id_resep,))
        cursor.execute("DELETE FROM steps WHERE recipe_id=%s", (id_resep,))
        for b in data['bahan']:
            cursor.execute("INSERT INTO ingredients (recipe_id, item_name, quantity, unit) VALUES (%s, %s, %s, %s)", (id_resep, b['nama'], b['jumlah'], b['satuan']))
        for idx, step in enumerate(data['langkah']):
            cursor.execute("INSERT INTO steps (recipe_id, step_number, instruction) VALUES (%s, %s, %s)", (id_resep, idx+1, step))
        conn.commit()
        return {"sukses": True, "pesan": "Update Berhasil!"}
    except Exception as e: return {"sukses": False, "pesan": str(e)}
    finally: conn.close()

@eel.expose
def ambil_semua_resep():
    conn = db.get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id, r.title, r.description, r.image_path, r.is_favorite, 
        GROUP_CONCAT(c.name SEPARATOR ', ') as category_name
        FROM recipes r 
        LEFT JOIN recipe_categories rc ON r.id = rc.recipe_id
        LEFT JOIN categories c ON rc.category_id = c.id
        GROUP BY r.id
        ORDER BY r.is_favorite DESC, r.created_at DESC
    """)
    res = cursor.fetchall()
    conn.close()
    return res

@eel.expose
def ambil_detail_resep(id_resep):
    conn = db.get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM recipes WHERE id=%s", (id_resep,))
    resep = cursor.fetchone()
    if resep:
        cursor.execute("SELECT c.id, c.name FROM categories c JOIN recipe_categories rc ON c.id = rc.category_id WHERE rc.recipe_id = %s", (id_resep,))
        resep['categories'] = cursor.fetchall()
        cursor.execute("SELECT * FROM ingredients WHERE recipe_id=%s", (id_resep,))
        resep['bahan'] = cursor.fetchall()
        cursor.execute("SELECT * FROM steps WHERE recipe_id=%s ORDER BY step_number ASC", (id_resep,))
        resep['langkah'] = cursor.fetchall()
    conn.close()
    return resep

@eel.expose
def hapus_resep(id_resep):
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        # === TAMBAHAN: HAPUS GAMBAR SAAT RESEP DIHAPUS ===
        cursor.execute("SELECT image_path FROM recipes WHERE id=%s", (id_resep,))
        row = cursor.fetchone()
        if row and row['image_path']:
            full_path = os.path.join("web", row['image_path'])
            if os.path.exists(full_path):
                os.remove(full_path)
        # ==================================================

        cursor.execute("DELETE FROM recipes WHERE id = %s", (id_resep,))
        conn.commit()
        return {"sukses": True, "pesan": "Resep dihapus."}
    except Exception as e: return {"sukses": False, "pesan": str(e)}
    finally: conn.close()

@eel.expose
def toggle_favorite(id_resep, status_baru):
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor()
        val = 1 if status_baru else 0
        cursor.execute("UPDATE recipes SET is_favorite=%s WHERE id=%s", (val, id_resep))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# --- 4. MEAL PLANNER ---
@eel.expose
def ambil_rencana_mingguan():
    conn = db.get_db_connection()
    if not conn: return {}
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT mp.id as plan_id, mp.day_name, mp.meal_type, 
               r.id as recipe_id, r.title, r.image_path 
        FROM meal_plans mp
        JOIN recipes r ON mp.recipe_id = r.id
    """)
    hasil = cursor.fetchall()
    conn.close()
    
    output = {}
    days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    types = ['Sarapan', 'Siang', 'Malam']
    for d in days:
        output[d] = {}
        for t in types: output[d][t] = None
    for row in hasil:
        d = row['day_name']
        t = row['meal_type']
        if d in output and t in output[d]: output[d][t] = row
    return output

@eel.expose
def simpan_rencana(recipe_id, day, meal_type):
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM meal_plans WHERE day_name=%s AND meal_type=%s", (day, meal_type))
        cursor.execute("INSERT INTO meal_plans (recipe_id, day_name, meal_type) VALUES (%s, %s, %s)", (recipe_id, day, meal_type))
        conn.commit()
        return {"sukses": True}
    except Exception as e: return {"sukses": False, "pesan": str(e)}
    finally: conn.close()

@eel.expose
def hapus_rencana(plan_id):
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM meal_plans WHERE id=%s", (plan_id,))
        conn.commit()
        return {"sukses": True}
    except: return {"sukses": False}
    finally: conn.close()

eel.start('index.html', size=(1100, 750))