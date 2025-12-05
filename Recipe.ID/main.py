import eel
import db
import base64
import os
import time
import datetime
import sqlite3 # Pastikan ini ada

eel.init('web')

# --- FUNGSI BARU: INISIALISASI DB SQLite ---
def init_db():
    conn = db.get_db_connection()
    if not conn:
        print("Gagal menginisialisasi database.")
        return

    # Skema SQL dan Data Awal yang diambil dari file recipe_id.sql
    # Semua INTEGER PRIMARY KEY AUTOINCREMENT
    sql_schema_and_data = """
-- Struktur dari tabel `categories`
CREATE TABLE IF NOT EXISTS `categories` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` varchar(50) NOT NULL
);
INSERT OR IGNORE INTO `categories` (`id`, `name`) VALUES
(1, 'Sarapan'),
(2, 'Makan Siang'),
(3, 'Makan Malam'),
(4, 'Cemilan'),
(5, 'Minuman');

-- Struktur dari tabel `recipes`
CREATE TABLE IF NOT EXISTS `recipes` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `title` varchar(100) NOT NULL,
  `description` text,
  `servings` int DEFAULT 1,
  `image_path` varchar(255) DEFAULT NULL,
  `is_favorite` tinyint(1) DEFAULT 0,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO `recipes` (`id`, `title`, `description`, `servings`, `image_path`, `is_favorite`, `created_at`) VALUES
(2, 'Ocean Blue Drink', 'Ocean Blue Drink adalah minuman berwarna biru cerah yang biasanya dibuat dari campuran sirup blue curaçao (non-alkohol), lemon atau jeruk, dan soda. Rasanya segar, manis-asam, dengan tampilan yang menyerupai warna laut sehingga cocok sebagai minuman penyegar.', 1, 'assets/uploaded/1764878257.png', 0, '2025-12-04 19:55:59'),
(3, 'Stik Kentang Goreng Keju', 'Stik Kentang Goreng Keju adalah camilan gurih yang dibuat dari adonan kentang halus yang dicampur keju, kemudian dibentuk memanjang seperti stik dan digoreng hingga renyah. Rasanya perpaduan renyah di luar, lembut di dalam, dengan aroma keju yang kuat, sehingga cocok sebagai snack atau teman santai.', 1, 'assets/uploaded/1764878914.jpg', 1, '2025-12-04 20:07:20'),
(4, 'Ayam Kecap Pedas', 'Ayam kecap pedas adalah masakan ayam dengan kecap manis yang dipadukan cabai, menghasilkan rasa manis, gurih, dan pedas yang nikmat serta cocok disajikan dengan nasi hangat.', 1, 'assets/uploaded/1764883877.jpg', 1, '2025-12-04 21:31:17'),
(5, 'Mie Goreng Khas Aceh', 'Mie Goreng Khas Aceh adalah hidangan mie berbumbu kuat dari Aceh yang dimasak dengan rempah-rempah khas seperti bawang, cabai, kari, dan kecap. Mie bertekstur tebal ini digoreng bersama potongan daging (biasanya sapi atau ayam), sayuran, serta sedikit kuah rempah yang meresap, menghasilkan rasa pedas, gurih, dan aromatik.', 1, 'assets/uploaded/1764884539.jpg', 0, '2025-12-04 21:40:06'),
(6, 'Nasi Goreng Kampung', 'Nasi Goreng Kampung adalah nasi goreng tradisional khas Indonesia yang dimasak dengan bumbu sederhana seperti bawang, cabai, terasi, dan kecap sedikit atau tanpa kecap. Ciri khasnya memiliki rasa gurih-pedas dengan aroma smokey, biasanya disajikan dengan irisan mentimun, kerupuk, dan telur.', 1, 'assets/uploaded/1764884926.jpg', 0, '2025-12-04 21:48:46'),
(7, 'Martabak Mini: Telur dan Sawi', 'Martabak Mini Telur dan Sawi adalah jajanan gurih berukuran kecil yang dibuat dari kulit martabak tipis berisi campuran telur dan irisan sawi. Saat digoreng, kulitnya menjadi renyah sementara isian tetap lembut dan savory. Rasanya sederhana namun nikmat, cocok sebagai camilan atau lauk pendamping.', 1, 'assets/uploaded/1764885202.jpg', 0, '2025-12-04 21:53:22');

-- Struktur Ingredients
CREATE TABLE IF NOT EXISTS `ingredients` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `recipe_id` int,
  `item_name` varchar(100),
  `quantity` varchar(50),
  `unit` varchar(50),
  FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE
);
INSERT INTO `ingredients` (`id`, `recipe_id`, `item_name`, `quantity`, `unit`) VALUES
(90, 2, 'Sirup Jeruk', '4', 'sdm'), (91, 2, 'Sprite', '120', 'ml'), (92, 2, 'Pewarna Makanan Biru', '1', 'tetes'), (93, 2, 'Ice Cube', '8', 'buah'), (94, 2, 'Biji Selasih,', '1/2', 'sdm'), (103, 3, 'Kentang', '800', 'gram'), (104, 3, 'Keju Cheddar Parut', '50', 'gram'), (105, 3, 'Kaldu bubuk', 'Secukupnya', ''), (106, 3, 'Garam', 'Secukupnya', ''), (107, 3, 'Lada', 'Secukupnya', ''), (108, 3, 'Parsley Kering', 'Secukupnya', ''), (109, 3, 'Tepung Maizena', '150', 'gram'), (110, 3, 'Minyak ', '1,5', 'liter'), (175, 7, 'Telur', '2', 'butir'), (176, 7, 'Kulit Lumpia', '6', 'lembar'), (177, 7, 'Bawang Merah', '4', 'siung'), (178, 7, 'Bawang Putih', '2', 'siung'), (179, 7, 'Sawi Caisim (ambil daunnya saja)', '1', 'ikat'), (180, 7, 'Garam', 'Secukupnya', ''), (181, 7, 'Penyedap', 'Secukupnya', ''), (182, 7, 'Minyak Goreng Rose Brand', 'Secukupnya', ''), (193, 5, 'Mie Kuning Basah', '1', 'kg'), (194, 5, 'Mumbu Mie Aceh', '5', 'sdm'), (195, 5, 'Kol', '1/4', 'kg'), (196, 5, 'Toge', '200', 'gram'), (197, 5, 'Daun Bawang Iris', '2', 'batang'), (198, 5, 'Daun Seledri Iris', '1', 'ikat kecil'), (199, 5, 'Minyak goreng Rose Brand', 'Secukupnya', ''), (200, 5, 'Bawang Merah Iris', '3', 'suing'), (201, 5, 'Udang', '100', 'gram'), (202, 5, 'Tomat Iris', '1', 'buah'), (203, 5, 'Garam', '2', 'sdm'), (204, 5, 'Asatu Rose Brand', '1', 'sdt'), (205, 5, 'Kecap Manis', '3', 'sdm'), (206, 5, 'Saos Tiram', '2', 'sdm'), (207, 5, 'Lada Bubuk', '1/4', 'sdt'), (208, 5, 'Air', '100', 'ml'), (229, 6, 'Nasi', '1', 'piring'), (230, 6, 'Cabe Rawit Merah, Iris Tipis', '5', 'buah'), (231, 6, 'Bawang Merah, Iris Tipis', '5', 'siung'), (232, 6, 'Bawang Putih, Iris Tipis', '3', 'siung'), (233, 6, 'Telur, Kocok Lepas', '1', 'butir'), (234, 6, 'Kecap Manis Indofood', '1', 'sdm'), (235, 6, 'Kecap Ikan', '1', 'sdm'), (236, 6, 'Garam', '1/2', 'sdt'), (237, 6, 'Gula Pasir', '1/2', 'sdt'), (238, 6, 'Lada Bubuk', '1/2', 'sdt'), (239, 4, 'Ayam', '1', 'kg'), (240, 4, 'Bawang Bombay', '1', 'buah'), (241, 4, 'Kecap Manis', '6', 'sdm'), (242, 4, 'Bawang Merah', '7', 'siung'), (243, 4, 'Bawang Putih', '3', 'siung'), (244, 4, 'Cabe Rawit Hijau', '100', 'gram'), (245, 4, 'Cabe Rawit Merah', '10', 'buah'), (246, 4, 'Daun Jeruk', '4', 'lembar'), (247, 4, 'Kayu Manis', '1', 'batang'), (248, 4, 'Kapulaga', '3', 'buah'), (249, 4, 'Ketumbar', '2', 'sdm'), (250, 4, 'Cengkeh', '4', 'cengkeh'), (251, 4, 'Kemiri', '2', 'buah'), (252, 4, 'Lawang', '1', 'bunga');

-- Struktur Recipe Categories
CREATE TABLE IF NOT EXISTS `recipe_categories` (
  `recipe_id` int NOT NULL,
  `category_id` int NOT NULL,
  PRIMARY KEY (`recipe_id`, `category_id`),
  FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE
);
INSERT INTO `recipe_categories` (`recipe_id`, `category_id`) VALUES
(2, 5), (3, 4), (4, 2), (4, 3), (5, 2), (5, 3), (5, 4), (6, 1), (6, 2), (7, 2), (7, 4);

-- Struktur Steps
CREATE TABLE IF NOT EXISTS `steps` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `recipe_id` int,
  `step_number` int,
  `instruction` text,
  FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE
);
INSERT INTO `steps` (`id`, `recipe_id`, `step_number`, `instruction`) VALUES
(40, 2, 1, 'Siapkan gelas saji (menggunakan gelas saji tinggi volume 350 ml), lalu tuangi sirup jeruk.'), (41, 2, 2, 'Tambahkan ice cube (atau sampai memenuhi gelas), lanjut tuangi larutan sprite biru perlahan.'), (42, 2, 3, 'Terakhir tambahkan biji selasih, siap untuk di sajikan, aduk terlebih dahulu sebelum di minum.'), (47, 3, 1, 'Kupas kentang, rendam dalam air garam, cuci bersih potong-potong, rebus sampai matang, haluskan.'), (48, 3, 2, 'Dalam adonan kentang masukkan keju parut, kaldu bubuk, garam dan lada, aduk-aduk, tuang tepung maizena dan parsley kering, aduk sampai rata.'), (49, 3, 3, 'Gilas adonan, rapikan kemudian potong-potong bentuk stik.'), (50, 3, 4, 'Goreng dalam minyak panas sampai kuning kecoklatan.'), (74, 7, 1, 'Siapkan bahan. Iris bawang merah dan bawang putih. Rajang daun sawi.'), (75, 7, 2, 'Panaskan Minyak Goreng Rose Brand dan tumis bawang merah- bawang putih hingga layu. Jika sudah layu, masukkan daun sawi.'), (76, 7, 3, 'Masukkan garam dan penyedap. Kemudian masukkan 2 butir telur ayam. Kocok lepas di tumisan sawi. Tumis hingga telur setengah matang, kemudian matikan kompor.'), (77, 7, 4, 'Angkat. Kemudian masukkan isian ke dalam kulit lumpia. Gulung sesuai selera, atau seperti di gambar.'), (78, 7, 5, 'Panaskan Minyak Goreng Rose Brand. Goreng martabak hingga kecoklatan. Sebagai tips, jangan terlalu sering membalik martabak agar tidak terlalu berminyak. Angkat dan tiriskan. Martabak mini siap disajikan.'), (83, 5, 1, 'Siapkan bahan, tuangkan minyak goreng Rose Brand ke dalam wajan agak besar. Tumis bawang merah hingga harum, masukkan tomat dan udang, aduk rata'), (84, 5, 2, 'Masukkan bumbu mie Aceh yang sudah di tumis. Tambahkan air sedikit agar tidak gosong. Masukkan kol iris dan toge.'), (85, 5, 3, 'Beri garam, kecap, saos tiram, Asatu, lada. Aduk rata. Masukkan mie, aduk aduk, saya menggunakan dua Sutil agar mudah diaduk.'), (86, 5, 4, 'Masukkan daun seledri dan daun bawang. Aduk kembali, jangan lupa cek rasa. Sajikan. Enak... Ada kerupuk, timun. Taburi bawang goreng, behhhh, Pas lagi ada acar lebih mantap. Selamat mencoba.'), (95, 6, 1, 'Siapkan bahan-bahannya.'), (96, 6, 2, 'Kocok telur, beri sedikit garam. Panaskan minyak diwajan masukkan telur bikin orak arik, sisihkan'), (97, 6, 3, 'Dengan sisa minyak, tumis bawang merah, bawang putih dan cabe rawit hingga harum. Masukkan nasi putih, telur orak arik. Beri Kecap Manis Indofood, gula, garam dan lada.'), (98, 6, 4, 'Masak sambil terus diaduk sampai merata dan nasi agak kering. Koreksi rasanya. Angkat pindahkan kepiting saji. Sajikan dengan pelengkap taburan bawang goreng, telur ceplok, irisan mentimun dan tomat.'), (99, 4, 1, 'Goreng ayam sampai 3/4 kering. Potong-potong bawang bombay'), (100, 4, 2, 'Haluskan semua bahan-bahan bumbu'), (101, 4, 3, 'Masukkan minyak ke wajan, tumis bawang bombay dan saat sudah sedikit layu kemudian masukkan bumbu halus'), (102, 4, 4, 'Masak bumbu hingga pecah minyak, kemudian masukkan 7 sdm kecap manis'), (103, 4, 5, 'Kasih garam, penyedap rasa, dan sedikit gula.'), (104, 4, 6, 'Masukkan ayam yang sudah di goreng, tutup panci selama 10 menit supaya bumbu meresap.');

-- Struktur Meal Plans
CREATE TABLE IF NOT EXISTS `meal_plans` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `recipe_id` int,
  `day_name` varchar(20),
  `meal_type` varchar(20),
  FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE
);
INSERT INTO `meal_plans` (`id`, `recipe_id`, `day_name`, `meal_type`) VALUES
(9, 6, 'Senin', 'Sarapan'), (10, 5, 'Senin', 'Malam'), (11, 4, 'Jumat', 'Siang'), (12, 3, 'Rabu', 'Siang'), (13, 2, 'Kamis', 'Malam'), (14, 7, 'Selasa', 'Sarapan');
    """
    
    cursor = conn.cursor()
    
    # Cek apakah tabel 'recipes' sudah ada dengan cara yang lebih aman untuk SQLite
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recipes'")
        if cursor.fetchone() is None:
             # Jika belum ada, jalankan skema lengkap
            cursor.executescript(sql_schema_and_data)
            print("Database SQLite berhasil diinisialisasi.")
    except Exception as e:
        print(f"Error saat cek/inisialisasi tabel: {e}")
        
    conn.commit()
    conn.close()

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
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM recipes")
        stats_resep = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM categories")
        stats_kat = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM recipes WHERE is_favorite = 1")
        stats_fav = cursor.fetchone()['total']

        cursor.execute("SELECT id, title, description, image_path FROM recipes ORDER BY RANDOM() LIMIT 3")
        rekomendasi = cursor.fetchall()

        cursor.execute("""
            SELECT r.id, r.title, r.image_path 
            FROM recipes r
            JOIN recipe_categories rc ON r.id = rc.recipe_id
            JOIN categories c ON rc.category_id = c.id
            WHERE c.name = 'Cemilan'
            ORDER BY RANDOM() LIMIT 5
        """)
        rek_cemilan = cursor.fetchall()

        cursor.execute("""
            SELECT r.id, r.title, r.image_path 
            FROM recipes r
            JOIN recipe_categories rc ON r.id = rc.recipe_id
            JOIN categories c ON rc.category_id = c.id
            WHERE c.name = 'Minuman'
            ORDER BY RANDOM() LIMIT 5
        """)
        rek_minuman = cursor.fetchall()

        # NOTE: GROUP_CONCAT di MySQL adalah GROUP_CONCAT di SQLite
        cursor.execute("""
            SELECT r.id, r.title, r.image_path, r.created_at, 
            GROUP_CONCAT(c.name, ', ') as category_name
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
            WHERE mp.day_name = ?
        """, (hari_ini,))
        rencana_db = cursor.fetchall()

        rencana_struct = {'Sarapan': None, 'Siang': None, 'Malam': None}
        for r in rencana_db:
            # Karena row_factory sudah diatur, akses data seperti dictionary
            rencana_struct[r['meal_type']] = dict(r)

        conn.close()
        
        return {
            "stats": {"resep": stats_resep, "kategori": stats_kat, "favorit": stats_fav},
            "rekomendasi": [dict(r) for r in rekomendasi],
            "cemilan": [dict(r) for r in rek_cemilan],
            "minuman": [dict(r) for r in rek_minuman],
            "terbaru": [dict(r) for r in terbaru],
            "rencana_hari_ini": {"hari": hari_ini, "menu": rencana_struct},
            "status": "Terkoneksi"
        }
    return {"status": "Error Database"}

# --- 2. KATEGORI ---
@eel.expose
def ambil_kategori():
    conn = db.get_db_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY name ASC")
    res = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return res

@eel.expose
def tambah_kategori_baru(nama):
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (nama,))
        conn.commit()
        return {"sukses": True, "pesan": "Kategori ditambah!"}
    except Exception as e: return {"sukses": False, "pesan": str(e)}
    finally: conn.close()

@eel.expose
def hapus_kategori(id_kat):
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id=?", (id_kat,))
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
        query = "INSERT INTO recipes (title, description, servings, image_path) VALUES (?, ?, ?, ?)"
        val = (data['judul'], data['deskripsi'], 1, path_gambar)
        cursor.execute(query, val)
        resep_id = cursor.lastrowid
        for kat_id in data['kategori_ids']:
            cursor.execute("INSERT INTO recipe_categories (recipe_id, category_id) VALUES (?, ?)", (resep_id, kat_id))
        for b in data['bahan']:
            cursor.execute("INSERT INTO ingredients (recipe_id, item_name, quantity, unit) VALUES (?, ?, ?, ?)", (resep_id, b['nama'], b['jumlah'], b['satuan']))
        for idx, step in enumerate(data['langkah']):
            cursor.execute("INSERT INTO steps (recipe_id, step_number, instruction) VALUES (?, ?, ?)", (resep_id, idx+1, step))
        conn.commit()
        return {"sukses": True, "pesan": "Resep tersimpan!"}
    except Exception as e: return {"sukses": False, "pesan": str(e)}
    finally: conn.close()

# --- UPDATE DENGAN FITUR HAPUS GAMBAR LAMA ---
@eel.expose
def update_resep_lama(id_resep, data):
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Proses Gambar Baru
        path_gambar_baru = proses_upload_gambar(data.get('nama_file'), data.get('file_base64'))
        
        if path_gambar_baru:
            # === LOGIC PENGHAPUSAN FILE LAMA ===
            cursor.execute("SELECT image_path FROM recipes WHERE id=?", (id_resep,))
            hasil_lama = cursor.fetchone()
            
            if hasil_lama and hasil_lama['image_path']:
                path_lama = hasil_lama['image_path']
                full_path_lama = os.path.join("web", path_lama)
                
                if os.path.exists(full_path_lama):
                    try:
                        os.remove(full_path_lama)
                        print(f"Berhasil menghapus file lama: {full_path_lama}")
                    except Exception as e_del:
                        print(f"Gagal hapus file: {e_del}")
            # ===================================

            # Update Database dengan Gambar Baru
            query = "UPDATE recipes SET title=?, description=?, image_path=? WHERE id=?"
            val = (data['judul'], data['deskripsi'], path_gambar_baru, id_resep)
        else:
            # Tidak ada gambar baru, update teks saja
            query = "UPDATE recipes SET title=?, description=? WHERE id=?"
            val = (data['judul'], data['deskripsi'], id_resep)
            
        cursor.execute(query, val)

        # Reset Kategori, Bahan, Langkah (Sama seperti sebelumnya)
        cursor.execute("DELETE FROM recipe_categories WHERE recipe_id=?", (id_resep,))
        for kat_id in data['kategori_ids']:
            cursor.execute("INSERT INTO recipe_categories (recipe_id, category_id) VALUES (?, ?)", (id_resep, kat_id))
        cursor.execute("DELETE FROM ingredients WHERE recipe_id=?", (id_resep,))
        cursor.execute("DELETE FROM steps WHERE recipe_id=?", (id_resep,))
        for b in data['bahan']:
            cursor.execute("INSERT INTO ingredients (recipe_id, item_name, quantity, unit) VALUES (?, ?, ?, ?)", (id_resep, b['nama'], b['jumlah'], b['satuan']))
        for idx, step in enumerate(data['langkah']):
            cursor.execute("INSERT INTO steps (recipe_id, step_number, instruction) VALUES (?, ?, ?)", (id_resep, idx+1, step))
        conn.commit()
        return {"sukses": True, "pesan": "Update Berhasil!"}
    except Exception as e: return {"sukses": False, "pesan": str(e)}
    finally: conn.close()

@eel.expose
def ambil_semua_resep():
    conn = db.get_db_connection()
    if not conn: return []
    cursor = conn.cursor()
    # NOTE: GROUP_CONCAT di MySQL adalah GROUP_CONCAT di SQLite
    cursor.execute("""
        SELECT r.id, r.title, r.description, r.image_path, r.is_favorite, 
        GROUP_CONCAT(c.name, ', ') as category_name
        FROM recipes r 
        LEFT JOIN recipe_categories rc ON r.id = rc.recipe_id
        LEFT JOIN categories c ON rc.category_id = c.id
        GROUP BY r.id
        ORDER BY r.is_favorite DESC, r.created_at DESC
    """)
    res = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return res

@eel.expose
def ambil_detail_resep(id_resep):
    conn = db.get_db_connection()
    if not conn: return None
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM recipes WHERE id=?", (id_resep,))
    resep = cursor.fetchone()
    
    if resep:
        resep = dict(resep) # Konversi ke dict agar bisa dimodifikasi
        
        cursor.execute("SELECT c.id, c.name FROM categories c JOIN recipe_categories rc ON c.id = rc.category_id WHERE rc.recipe_id = ?", (id_resep,))
        resep['categories'] = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM ingredients WHERE recipe_id=?", (id_resep,))
        resep['bahan'] = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM steps WHERE recipe_id=? ORDER BY step_number ASC", (id_resep,))
        resep['langkah'] = [dict(r) for r in cursor.fetchall()]
        
    conn.close()
    return resep

@eel.expose
def hapus_resep(id_resep):
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor()
        
        # === HAPUS GAMBAR SAAT RESEP DIHAPUS ===
        cursor.execute("SELECT image_path FROM recipes WHERE id=?", (id_resep,))
        row = cursor.fetchone()
        if row and row['image_path']:
            full_path = os.path.join("web", row['image_path'])
            if os.path.exists(full_path):
                os.remove(full_path)
        # ==================================================

        cursor.execute("DELETE FROM recipes WHERE id = ?", (id_resep,))
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
        cursor.execute("UPDATE recipes SET is_favorite=? WHERE id=?", (val, id_resep))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# --- 4. MEAL PLANNER ---
@eel.expose
def ambil_rencana_mingguan():
    conn = db.get_db_connection()
    if not conn: return {}
    cursor = conn.cursor()
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
        if d in output and t in output[d]: output[d][t] = dict(row) # Konversi ke dict
    return output

@eel.expose
def simpan_rencana(recipe_id, day, meal_type):
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM meal_plans WHERE day_name=? AND meal_type=?", (day, meal_type))
        cursor.execute("INSERT INTO meal_plans (recipe_id, day_name, meal_type) VALUES (?, ?, ?)", (recipe_id, day, meal_type))
        conn.commit()
        return {"sukses": True}
    except Exception as e: return {"sukses": False, "pesan": str(e)}
    finally: conn.close()

@eel.expose
def hapus_rencana(plan_id):
    conn = db.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM meal_plans WHERE id=?", (plan_id,))
        conn.commit()
        return {"sukses": True}
    except: return {"sukses": False}
    finally: conn.close()

init_db()

eel.start('index.html', size=(1100, 750))