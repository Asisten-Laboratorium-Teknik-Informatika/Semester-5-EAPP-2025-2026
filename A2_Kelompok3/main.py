import eel
import mysql.connector
import google.generativeai as genai
import json
import os
import base64
from werkzeug.security import generate_password_hash, check_password_hash

genai.configure(api_key="AIzaSyA0RJfz31PgOYMmqax4538I_mCodsYPxDw")

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'db_inventory'
}

if not os.path.exists('web/uploads'):
    os.makedirs('web/uploads')

eel.init('web')


@eel.expose
def register_user(username, password):
    check = run_query("SELECT id FROM users WHERE username = %s", (username,), fetch=True)
    if check:
        return {"status": "error", "msg": "Username sudah terdaftar!"}
    
    hashed_pw = generate_password_hash(password)

    sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
    result = run_query(sql, (username, hashed_pw))
    
    if "Error" in str(result):
        return {"status": "error", "msg": "Gagal mendaftar."}
    
    return {"status": "success", "msg": "Registrasi berhasil! Silakan login."}

@eel.expose
def login_user(username, password):
    user = run_query("SELECT * FROM users WHERE username = %s", (username,), fetch=True)
    
    if not user:
        return {"status": "error", "msg": "Username tidak ditemukan."}

    stored_hash = user[0]['password']
    if check_password_hash(stored_hash, password):
        return {"status": "success", "msg": "Login sukses!"}
    else:
        return {"status": "error", "msg": "Password salah!"}

# --- 2. DATABASE HELPER ---
def run_query(query, params=None, fetch=False):
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        
        if fetch:
            result = cursor.fetchall()
            return result
        
        conn.commit()
        return "Berhasil dieksekusi."
    except Exception as e:
        return f"Error Database: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- 3. FUNGSI UNTUK FILE UPLOAD ---
@eel.expose
def save_image_from_ui(filename, file_data):
    try:
        header, encoded = file_data.split(",", 1)
        data = base64.b64decode(encoded)
        file_path = f"web/uploads/{filename}"
        with open(file_path, "wb") as f:
            f.write(data)
        return f"uploads/{filename}" 
    except Exception as e:
        return f"Error Upload: {str(e)}"
    

def parse_indonesian_number(value):
    """
    Mengubah teks input user/AI menjadi angka float yang akurat.
    Contoh: "11juta" -> 11000000.0
            "1.5jt"  -> 1500000.0
            "500rb"  -> 500000.0
    """
    if isinstance(value, (int, float)):
        return float(value)
    
    s_val = str(value).lower().replace('rp', '').replace(',', '').strip()
    
    multiplier = 1
    if 'juta' in s_val or 'jt' in s_val:
        multiplier = 1_000_000
        s_val = s_val.replace('juta', '').replace('jt', '')
    elif 'milyar' in s_val or 'm' in s_val:
        multiplier = 1_000_000_000
        s_val = s_val.replace('milyar', '').replace('m', '')
    elif 'ribu' in s_val or 'rb' in s_val:
        multiplier = 1_000
        s_val = s_val.replace('ribu', '').replace('rb', '')
    
    try:
        if '.' in s_val and multiplier > 1:
            return float(s_val) * multiplier
        else:
            return float(s_val.replace('.', '')) * multiplier
    except:
        return 0.0

# --- 4. TOOLS UNTUK AI AGENT ---

def tool_get_all_products():
    """Mengambil semua data produk."""
    data = run_query("SELECT * FROM products ORDER BY id DESC", fetch=True)
    return json.dumps(data, default=str)

def tool_add_product(name, category, stock, price, image_url=None):
    """
    Menambahkan produk baru ke database.
    Mendukung input harga singkatan (misal: "15jt", "500rb").
    """

    final_price = parse_indonesian_number(price)
    final_stock = int(parse_indonesian_number(stock))

    if not image_url:
        image_url = "https://placehold.co/400x300?text=No+Image"

    sql = "INSERT INTO products (name, category, stock, price, sales, image_url) VALUES (%s, %s, %s, %s, 0, %s)"
    
    try:
        run_query(sql, (name, category, final_stock, final_price, image_url))
        return f"Berhasil! Produk '{name}' ditambahkan dengan harga Rp {final_price:,.0f} dan stok {final_stock}."
    except Exception as e:
        return f"Gagal menambahkan produk: {str(e)}"

def tool_update_stock(product_name, quantity_change):
    """Update stok (positif=tambah, negatif=kurang/jual)."""
    products = run_query("SELECT id, stock FROM products WHERE name LIKE %s LIMIT 1", (f"%{product_name}%",), fetch=True)
    
    if not products: return f"Produk '{product_name}' tidak ditemukan."
    
    pid = products[0]['id']
    new_stock = products[0]['stock'] + int(quantity_change)
    
    if new_stock < 0: return "Stok tidak cukup."

    if int(quantity_change) < 0:
        sql = "UPDATE products SET stock = %s, sales = sales + %s WHERE id = %s"
        run_query(sql, (new_stock, abs(int(quantity_change)), pid))
    else:
        sql = "UPDATE products SET stock = %s WHERE id = %s"
        run_query(sql, (new_stock, pid))
        
    return f"Berhasil. Stok {product_name} sekarang: {new_stock}."

def tool_delete_product(product_name):
    return run_query("DELETE FROM products WHERE name LIKE %s", (f"%{product_name}%",))

def tool_edit_product(target_name, new_name=None, new_price=None, new_category=None, new_stock=None, new_image_url=None):
    """
    Mengedit detail produk.
    """
    products = run_query("SELECT id FROM products WHERE name LIKE %s LIMIT 1", (f"%{target_name}%",), fetch=True)
    
    if not products:
        return f"Error: Produk '{target_name}' tidak ditemukan."
    
    pid = products[0]['id']
    updates = []
    params = []

    if new_name:
        updates.append("name = %s")
        params.append(new_name)
    
    if new_price:
        final_price = parse_indonesian_number(new_price)
        updates.append("price = %s")
        params.append(final_price)
        
    if new_category:
        updates.append("category = %s")
        params.append(new_category)
        
    if new_stock is not None:
        updates.append("stock = %s")
        params.append(int(new_stock))
        
    if new_image_url:
        updates.append("image_url = %s")
        params.append(new_image_url)

    if not updates:
        return "Tidak ada perubahan. Sebutkan apa yang ingin diubah."

    params.append(pid)
    sql = f"UPDATE products SET {', '.join(updates)} WHERE id = %s"
    run_query(sql, tuple(params))
    return f"Berhasil update '{target_name}'. Harga set ke: Rp {params[updates.index('price = %s')]:,.0f}" if new_price else f"Berhasil update '{target_name}'."

# Inisialisasi Agent
tools = [
    tool_get_all_products, 
    tool_add_product, 
    tool_update_stock, 
    tool_edit_product,
    tool_delete_product]
model = genai.GenerativeModel('gemini-2.5-flash', tools=tools)
chat_session = model.start_chat(enable_automatic_function_calling=True)

# --- 5. EEL INTERFACE ---
@eel.expose
def get_products_frontend():
    # Mengirim data sebagai JSON String
    data = run_query("SELECT * FROM products ORDER BY id DESC", fetch=True)
    return json.dumps(data, default=str)

@eel.expose
def send_message_to_agent(message):
    try:
        sys_prompt = """
        Anda adalah AI Inventory Manager & Business Analyst profesional.
        
        TUGAS UTAMA:
        1. Eksekusi Perintah: Gunakan tools (add, edit, update_stock) jika user meminta perubahan data.
        2. Analisis Data: Jika user meminta "Analisis", "Laporan", atau "Review Stok":
           - Panggil tool 'tool_get_all_products' untuk membaca data.
           - Analisis:
             a. Produk Terlaris (Sales tertinggi).
             b. Stok Kritis (Stock < 5).
             c. Dead Stock (Stock banyak tapi Sales 0).
             d. Total Aset (Stock * Price).
           - BERIKAN OUTPUT DALAM FORMAT HTML KHUSUS (Tanpa markdown ```html):
             Gunakan struktur ini:
             <div class='analysis-report'>
                <div class='report-header'>📊 Laporan Analisis AI</div>
                <div class='report-section'>
                    <strong>🔥 Produk Terlaris:</strong> [Nama Produk] ([Jumlah] terjual)
                </div>
                <div class='report-section'>
                    <strong>⚠️ Stok Menipis:</strong> [List produk stock < 5]
                </div>
                <div class='report-section'>
                    <strong>💤 Dead Stock (Perlu Diskon):</strong> [List produk sales 0]
                </div>
                <div class='report-suggestion'>
                    <strong>💡 Saran Strategi:</strong> [Saran singkat 1 kalimat]
                </div>
             </div>
        
        ATURAN LAIN:
        - Jika user input angka singkatan ("15jt", "500rb"), kirim raw string ke tool, jangan convert sendiri.
        - Jawab singkat dan padat untuk chat biasa.
        """
        response = chat_session.send_message(f"{sys_prompt} User Message: {message}")
        return response.text
    except Exception as e:
        return f"Error AI: {str(e)}"

eel.start('index.html', size=(1300, 900))