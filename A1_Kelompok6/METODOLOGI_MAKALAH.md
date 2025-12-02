# METODOLOGI PENGEMBANGAN SISTEM
## Aplikasi Desktop Absensi Karyawan dengan Face Detection

---

## 1. METODOLOGI PENELITIAN

### 1.1 Pendekatan Penelitian
Penelitian ini menggunakan pendekatan **Research and Development (R&D)** dengan metode pengembangan sistem berbasis **Waterfall Model** yang dimodifikasi. Tahapan pengembangan meliputi:
- Analisis Kebutuhan
- Perancangan Sistem
- Implementasi
- Pengujian
- Dokumentasi

### 1.2 Teknik Pengumpulan Data
- **Studi Literatur**: Mempelajari teknologi Eel Framework, MySQL, OpenCV, dan sistem absensi berbasis desktop
- **Observasi**: Mengamati kebutuhan sistem absensi manual yang ada
- **Eksperimen**: Pengujian langsung terhadap fitur-fitur yang dikembangkan

### 1.3 Alat dan Bahan
**Software:**
- Python 3.11+
- MySQL Server
- Visual Studio Code / IDE Python
- Web Browser (Chrome/Edge)

**Library Python:**
- `eel==0.17.0` - Framework untuk desktop app berbasis web
- `mysql-connector-python==9.0.0` - Koneksi database MySQL
- `opencv-python==4.10.0.84` - Face detection dan image processing
- `numpy==2.1.2` - Operasi matematika untuk image processing
- `Pillow==10.4.0` - Image manipulation
- `python-dotenv==1.0.1` - Environment variable management

---

## 2. ANALISIS KEBUTUHAN SISTEM

### 2.1 Analisis Fungsional
Sistem harus mampu:
1. **Autentikasi Pengguna**
   - Registrasi karyawan baru
   - Login dengan validasi username dan password
   - Manajemen session pengguna

2. **Manajemen Absensi**
   - Clock In dengan validasi waktu (terlambat jika > 08:30)
   - Clock Out dengan perhitungan total jam kerja
   - Multiple session per hari (bisa clock in/out beberapa kali)
   - Perhitungan real-time jam kerja yang sedang berlangsung

3. **Face Detection**
   - Verifikasi wajah sebelum clock in/out
   - Tampilan kamera real-time
   - Konfirmasi manual dengan tombol ESC

4. **Dashboard dan Laporan**
   - Tampilan profil karyawan
   - Statistik kehadiran hari ini
   - Daftar karyawan yang hadir hari ini
   - Recent Activity (riwayat clock in/out real-time)
   - Laporan harian dan bulanan
   - Export data ke CSV

### 2.2 Analisis Non-Fungsional
- **Performance**: Response time < 2 detik untuk operasi database
- **Usability**: Interface yang user-friendly dan intuitif
- **Security**: Password di-hash menggunakan SHA-256
- **Reliability**: Sistem dapat menangani error dengan graceful handling
- **Maintainability**: Kode terstruktur dengan pemisahan modul yang jelas

---

## 3. PERANCANGAN SISTEM

### 3.1 Arsitektur Sistem

#### 3.1.1 Arsitektur Umum
Sistem menggunakan arsitektur **Client-Server** dengan komponen:
- **Frontend**: HTML, CSS, JavaScript (folder `web/`)
- **Backend**: Python dengan Eel Framework (folder `logic/`)
- **Database**: MySQL (tabel `users` dan `attendance`)

#### 3.1.2 Alur Komunikasi
```
Frontend (HTML/JS) 
    ↕ (Eel Bridge)
Backend (Python/Eel)
    ↕ (mysql.connector)
Database (MySQL)
```

### 3.2 Perancangan Database

#### 3.2.1 Entity Relationship Diagram (ERD)
- **Tabel `users`**: Menyimpan data karyawan
- **Tabel `attendance`**: Menyimpan data absensi
- **Relasi**: One-to-Many (satu user bisa banyak attendance record)

#### 3.2.2 Struktur Tabel

**Tabel `users`:**
- `employee_id` (VARCHAR(50), PRIMARY KEY)
- `username` (VARCHAR(50), UNIQUE, NOT NULL)
- `password` (VARCHAR(255), NOT NULL) - di-hash SHA-256
- `name` (VARCHAR(100), NOT NULL)
- `role` (VARCHAR(20), DEFAULT 'employee')
- `department` (VARCHAR(100), DEFAULT '')
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

**Tabel `attendance`:**
- `id` (INT, AUTO_INCREMENT, PRIMARY KEY)
- `employee_id` (VARCHAR(50), NOT NULL, INDEX)
- `date` (DATE, NOT NULL, INDEX)
- `clock_in` (TIME, NULL)
- `clock_out` (TIME, NULL)
- `total_hours` (DECIMAL(5,2), DEFAULT 0)
- `is_late` (BOOLEAN, DEFAULT FALSE)
- `late_minutes` (INT, DEFAULT 0)
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

**Catatan Desain:**
- Tidak ada UNIQUE constraint pada `(employee_id, date)` untuk mendukung multiple session per hari
- `total_hours` dihitung secara dinamis untuk session yang masih berlangsung

### 3.3 Perancangan Modul Backend

#### 3.3.1 Struktur Modul
```
logic/
├── __init__.py          # Package initializer
├── database.py          # Koneksi dan migrasi database
├── auth.py              # Autentikasi (login/register)
├── attendance.py        # Logika absensi (clock in/out, laporan)
├── face_detection.py    # Face detection dengan OpenCV
└── utils.py             # Utility functions (session management)
```

#### 3.3.2 Deskripsi Modul

**`database.py`:**
- Fungsi `get_db_connection()`: Membuka koneksi ke MySQL
- Fungsi `init_database()`: Inisialisasi tabel dan migrasi schema
- Auto-migration untuk menambahkan kolom yang hilang
- Drop foreign key constraint yang tidak diperlukan

**`auth.py`:**
- `hash_password()`: Hash password dengan SHA-256
- `generate_employee_id()`: Generate ID otomatis (USER001, USER002, ...)
- `@eel.expose login_user()`: Validasi login
- `@eel.expose register_user()`: Registrasi user baru

**`attendance.py`:**
- `clock_in()`: Proses clock in dengan validasi waktu
- `clock_out()`: Proses clock out dengan perhitungan jam
- `get_current_status()`: Status absensi hari ini (real-time)
- `get_attendance_report()`: Laporan harian/bulanan
- `get_attendance_statistics()`: Statistik kehadiran
- `get_recent_activity()`: Aktivitas terbaru
- `search_attendance_records()`: Pencarian data absensi
- `export_attendance_to_csv()`: Export ke CSV

**`face_detection.py`:**
- `detect_face()`: Deteksi wajah dengan OpenCV
- Menggunakan Haar Cascade untuk deteksi wajah
- Tampilan window kamera real-time
- Konfirmasi dengan tombol ESC

**`utils.py`:**
- `CURRENT_USER_SESSION`: Variabel global untuk session
- `set_current_user()`: Set user yang sedang login
- `get_current_user()`: Get user yang sedang login

### 3.4 Perancangan Interface

#### 3.4.1 Halaman Login (`login.html`)
- Form username dan password
- Tombol "Login" dan link ke "Register"
- Validasi input di frontend dan backend
- Remember username dengan localStorage

#### 3.4.2 Halaman Register (`register.html`)
- Form: username, password, confirm password, name, department
- Validasi password match
- Auto-generate employee_id
- Redirect ke login setelah registrasi

#### 3.4.3 Dashboard (`index.html`)
- **Header**: Profil user (nama, department, employee_id)
- **Statistik Card**: 
  - Status kehadiran hari ini
  - Total jam kerja hari ini
  - Karyawan yang hadir hari ini
- **Recent Activity**: Timeline clock in/out real-time
- **Navigation**: Link ke Attendance dan Reports

#### 3.4.4 Halaman Attendance (`Attadance.html`)
- **Tombol Clock In/Out**: Dinamis berdasarkan status
- **Status Card**: 
  - Status saat ini (Clocked In/Out)
  - Jam kerja sesi saat ini
  - Total jam hari ini
  - Waktu clock in terakhir
- **Timeline**: Riwayat clock in/out hari ini
- **Statistik**: Grafik atau ringkasan

#### 3.4.5 Halaman Reports (`reports.html`)
- **Filter**: Tanggal, bulan, tahun
- **Tabel Laporan**: 
  - Tanggal, Clock In, Clock Out, Total Jam, Status (Terlambat/On Time)
- **Pencarian**: Search by date range atau employee
- **Export**: Tombol export ke CSV

### 3.5 Perancangan Alur Proses

#### 3.5.1 Alur Login
```
1. User input username & password
2. Frontend validasi (tidak kosong)
3. Backend hash password & query database
4. Jika valid → set session → redirect ke dashboard
5. Jika tidak valid → tampilkan error
```

#### 3.5.2 Alur Clock In
```
1. User klik "Clock In"
2. Face detection (buka kamera)
3. User tekan ESC untuk konfirmasi
4. Jika wajah terdeteksi → Backend clock_in()
5. Validasi: cek apakah ada session terbuka
6. Insert record ke database
7. Update UI (tombol → "Clock Out", status → "Clocked In")
8. Redirect ke dashboard (opsional)
```

#### 3.5.3 Alur Clock Out
```
1. User klik "Clock Out"
2. Face detection (buka kamera)
3. User tekan ESC untuk konfirmasi
4. Jika wajah terdeteksi → Backend clock_out()
5. Update record terakhir (set clock_out, hitung total_hours)
6. Update UI (tombol → "Clock In", status → "Clocked Out")
```

#### 3.5.4 Alur Perhitungan Total Jam
```
1. Query database: ambil semua record hari ini
2. Untuk setiap record:
   - Jika clock_out NULL → hitung dari clock_in sampai sekarang
   - Jika clock_out ada → hitung dari clock_in sampai clock_out
3. Jumlahkan semua total jam
4. Tampilkan di UI (real-time update setiap 5 detik)
```

---

## 4. IMPLEMENTASI

### 4.1 Setup Environment
1. Install Python 3.11+
2. Install MySQL Server
3. Buat virtual environment: `python -m venv .venv`
4. Aktifkan virtual environment: `.venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -r requirements.txt`

### 4.2 Konfigurasi Database
1. Edit `logic/database.py`: sesuaikan `DB_CONFIG` (host, user, password)
2. Jalankan `main.py` → database dan tabel akan dibuat otomatis
3. User default: username `user`, password `password` (employee_id: USER001)

### 4.3 Implementasi Fitur

#### 4.3.1 Autentikasi
- **Registrasi**: Data langsung disimpan ke database (tidak ke localStorage)
- **Login**: Validasi password hash, set session di backend dan frontend
- **Session Management**: 
  - Backend: `CURRENT_USER_SESSION` (variabel global)
  - Frontend: `sessionStorage` untuk `currentUser` dan `isLoggedIn`

#### 4.3.2 Absensi
- **Multiple Session**: User bisa clock in/out beberapa kali per hari
- **Validasi Terlambat**: Jika clock_in > 08:30 → `is_late = TRUE`, hitung `late_minutes`
- **Real-time Calculation**: 
  - `current_session_hours`: Jam sesi yang sedang berlangsung
  - `today_total_hours`: Total jam hari ini (semua session)
- **Auto-refresh**: UI update setiap 5 detik dengan `setInterval`

#### 4.3.3 Face Detection
- **Library**: OpenCV dengan Haar Cascade (`haarcascade_frontalface_default.xml`)
- **Proses**:
  1. Buka kamera (index 0)
  2. Deteksi wajah dengan `detectMultiScale()`
  3. Tampilkan bounding box hijau jika wajah terdeteksi
  4. Tunggu user tekan ESC
  5. Jika ESC ditekan + wajah terdeteksi → return success
  6. Jika tidak → return failure
- **Error Handling**: Jika kamera tidak tersedia, tampilkan error message

#### 4.3.4 Dashboard & Laporan
- **Recent Activity**: Query `attendance` ORDER BY `created_at` DESC, limit 10
- **Karyawan Hadir**: Query semua user yang clock_in hari ini (clock_out bisa NULL)
- **Reports**: Filter by date range, hitung total jam dinamis
- **Export CSV**: Generate file di folder `exports/` dengan timestamp

### 4.4 Error Handling
- **Database Error**: Try-catch di setiap fungsi, return error message
- **Face Detection Error**: Validasi kamera tersedia, return error jika gagal
- **Session Error**: Redirect ke login jika session tidak valid
- **Input Validation**: Validasi di frontend (JavaScript) dan backend (Python)

---

## 5. PENGUJIAN

### 5.1 Pengujian Unit (Unit Testing)
**Modul yang diuji:**
- `auth.py`: Login, register, hash password
- `attendance.py`: Clock in/out, perhitungan jam, validasi terlambat
- `database.py`: Koneksi database, migrasi schema
- `face_detection.py`: Deteksi wajah, error handling kamera

### 5.2 Pengujian Integrasi (Integration Testing)
**Skenario:**
1. **Login → Dashboard**: Verifikasi data user tampil di dashboard
2. **Clock In → Face Detection**: Verifikasi wajah terdeteksi sebelum clock in
3. **Clock In → Clock Out**: Verifikasi total jam terhitung dengan benar
4. **Multiple Session**: Verifikasi bisa clock in/out beberapa kali per hari
5. **Reports**: Verifikasi laporan menampilkan data yang benar

### 5.3 Pengujian Sistem (System Testing)
**Skenario:**
1. **Flow Lengkap**: Register → Login → Clock In → Clock Out → Reports
2. **Edge Cases**:
   - Clock in tanpa face detection → harus gagal
   - Clock out tanpa clock in → harus gagal
   - Clock in saat sudah clock in (session terbuka) → error message
   - Clock in lewat jam 08:30 → status terlambat
3. **Performance**: Response time < 2 detik untuk semua operasi
4. **Usability**: Interface mudah digunakan, error message jelas

### 5.4 Hasil Pengujian
**Fitur yang Berhasil:**
- ✅ Login dan registrasi dengan validasi
- ✅ Clock in/out dengan face detection
- ✅ Perhitungan total jam real-time
- ✅ Multiple session per hari
- ✅ Validasi terlambat (jam 08:30)
- ✅ Dashboard dengan recent activity
- ✅ Laporan dan export CSV
- ✅ Auto-migration database

**Bug yang Diperbaiki:**
- ✅ Button status tidak update setelah clock in/out
- ✅ Total jam tidak reset saat login
- ✅ Face detection tidak menampilkan kamera
- ✅ Error database saat kolom tidak ada (auto-migration)
- ✅ Session tidak ter-update setelah registrasi

---

## 6. DOKUMENTASI

### 6.1 Dokumentasi Kode
- Setiap modul memiliki docstring
- Fungsi memiliki type hints
- Komentar pada logika yang kompleks

### 6.2 Dokumentasi Pengguna
- File `README.md` berisi:
  - Instalasi dan setup
  - Cara menjalankan aplikasi
  - Konfigurasi database
  - Troubleshooting

### 6.3 Dokumentasi Database
- ERD (Entity Relationship Diagram)
- Daftar tabel dan kolom
- Relasi antar tabel
- Index dan constraint

---

## 7. KESIMPULAN METODOLOGI

Metodologi pengembangan sistem ini menggunakan pendekatan **Waterfall Model** yang dimodifikasi dengan tahapan:
1. **Analisis Kebutuhan**: Identifikasi kebutuhan fungsional dan non-fungsional
2. **Perancangan**: Arsitektur sistem, database, modul, dan interface
3. **Implementasi**: Pengembangan kode dengan pemisahan modul yang jelas
4. **Pengujian**: Unit testing, integration testing, dan system testing
5. **Dokumentasi**: Dokumentasi kode, pengguna, dan database

**Keunggulan Metodologi:**
- Struktur kode terorganisir dengan pemisahan modul yang jelas
- Auto-migration database untuk kemudahan deployment
- Error handling yang robust di setiap layer
- Real-time update untuk pengalaman pengguna yang baik
- Face detection dengan konfirmasi manual untuk keamanan

**Keterbatasan:**
- Face detection belum menggunakan face recognition (hanya deteksi wajah)
- Belum ada fitur admin untuk manage user
- Belum ada notifikasi/reminder untuk clock in/out

---

## REFERENSI TEKNOLOGI

1. **Eel Framework**: https://github.com/ChrisKnott/Eel
2. **MySQL Connector Python**: https://dev.mysql.com/doc/connector-python/en/
3. **OpenCV Python**: https://opencv-python-tutroals.readthedocs.io/
4. **Python Documentation**: https://docs.python.org/3/

---

**Catatan untuk Penulis Makalah:**
- Sesuaikan format dengan template makalah yang digunakan
- Tambahkan diagram (ERD, Flowchart, Use Case) jika diperlukan
- Lengkapi dengan hasil pengujian yang lebih detail
- Tambahkan screenshot aplikasi untuk dokumentasi visual

