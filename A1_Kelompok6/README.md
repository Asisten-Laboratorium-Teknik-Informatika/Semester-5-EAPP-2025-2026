# AttendanceHub (Desktop Eel)

Sistem absensi sederhana berbasis Python + Eel yang terhubung dengan MySQL
(XAMPP). Proyek ini menyediakan fitur:

- Registrasi & login karyawan (password SHA-256).
- Clock in/out dengan validasi jam kerja (08:30–17:00) dan deteksi keterlambatan.
- Dashboard real-time (jam kerja, status aktif).
- Laporan & analitik (rekap jam kerja, ekspor CSV, pencarian).
- Sinkronisasi multi-tab melalui `localStorage` event.

## Menjalankan proyek

1. Pastikan Python 3.11+ dan MySQL (XAMPP) aktif.
2. Install dependency:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```
3. Jalankan backend:
   ```bash
   python main.py
   ```
4. Browser/desktop window akan terbuka pada `login.html` (port default 8085).

> Inisialisasi database dilakukan otomatis (membuat DB `attendance_db` dan user
> default `USER001`/`user`/`password`).

## Struktur penting

- `logic/database.py` – koneksi & migrasi MySQL.
- `logic/auth.py` – login/register + exposure Eel.
- `logic/attendance.py` – seluruh logika absensi, laporan, analitik.
- `logic/face_detection.py` – deteksi wajah OpenCV (fallback jika kamera tidak ada).
- `web/` – aset frontend (HTML, CSS, JS).

## Konfigurasi

Sesuaikan kredensial database di `logic/database.py` (`DB_CONFIG`). Bila ingin
mengubah jam kerja, update konstanta `WORK_START_TIME`, `WORK_END_TIME`, dan
`EXPECTED_CLOCK_IN` di `logic/attendance.py`.

## Troubleshooting

- **Tidak bisa konek DB** – pastikan MySQL aktif dan user/password sesuai.
- **Camera error** – modul `face_detection` otomatis fallback, namun Anda bisa
  menonaktifkan pengecekan wajah pada frontend bila diperlukan.
- **Laporan kosong** – pastikan rentang tanggal benar dan sudah ada data clock in.









