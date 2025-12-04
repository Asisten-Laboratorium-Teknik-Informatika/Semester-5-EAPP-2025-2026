-- ============================================
-- SQL QUERY UNTUK TABEL USERS
-- Sistem Parkir Modern - Authentication
-- ============================================

-- Buat tabel users jika belum ada
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nama_lengkap VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Buat index untuk performa
CREATE INDEX IF NOT EXISTS idx_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_role ON users(role);

-- ============================================
-- CONTOH DATA UNTUK TESTING (OPSIONAL)
-- ============================================

-- Insert user admin contoh (password: admin123)
-- Password di-hash dengan SHA256: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
-- Untuk testing, gunakan fungsi register di aplikasi atau hash password manual

-- Contoh query untuk insert user manual (password harus di-hash dulu):
-- INSERT INTO users (username, email, password, nama_lengkap, role) 
-- VALUES ('admin', 'admin@parkir.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Administrator', 'admin');

-- ============================================
-- QUERY UNTUK CEK DATA
-- ============================================

-- Lihat semua users
-- SELECT id, username, email, nama_lengkap, role, created_at FROM users;

-- Cari user berdasarkan username
-- SELECT * FROM users WHERE username = 'username_anda';

-- Cari user berdasarkan email
-- SELECT * FROM users WHERE email = 'email@example.com';

-- ============================================
-- QUERY UNTUK UPDATE DATA
-- ============================================

-- Update nama lengkap user
-- UPDATE users SET nama_lengkap = 'Nama Baru' WHERE id = 1;

-- Update password user (harus di-hash dulu)
-- UPDATE users SET password = 'hash_password_baru' WHERE id = 1;

-- Update role user
-- UPDATE users SET role = 'admin' WHERE id = 1;

-- ============================================
-- QUERY UNTUK HAPUS DATA
-- ============================================

-- Hapus user berdasarkan ID
-- DELETE FROM users WHERE id = 1;

-- Hapus semua users (HATI-HATI!)
-- DELETE FROM users;

-- ============================================
-- CATATAN PENTING
-- ============================================
-- 1. Password disimpan dalam bentuk hash SHA256
-- 2. Username dan email harus UNIQUE (tidak boleh duplikat)
-- 3. Role default adalah 'user', bisa diubah ke 'admin'
-- 4. created_at dan updated_at otomatis di-update oleh MySQL
-- 5. Untuk keamanan, jangan pernah menyimpan password dalam bentuk plain text
-- ============================================

