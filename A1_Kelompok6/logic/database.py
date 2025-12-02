"""
Manajemen koneksi dan migrasi database MySQL.
"""

from __future__ import annotations

import hashlib
from typing import Dict, Optional

import mysql.connector  # type: ignore
from mysql.connector import Error  # type: ignore

DB_CONFIG: Dict[str, object] = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
    "database": "attendance_db",
}

DATABASE_NAME = DB_CONFIG["database"]


def get_db_connection():
    """Buka koneksi ke database attendance."""
    try:
        config = DB_CONFIG.copy()
        return mysql.connector.connect(**config)  # type: ignore[arg-type]
    except Error as exc:  # pragma: no cover - hanya logging
        print(f"❌ Error connecting to database: {exc}")
        return None


def _column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(f"SHOW COLUMNS FROM {table} LIKE %s", (column,))
    return cursor.fetchone() is not None


def init_database() -> bool:
    """Inisialisasi database + migrasi ringan jika diperlukan."""
    try:
        config = DB_CONFIG.copy()
        database = config.pop("database")

        # Connect tanpa memilih database dulu
        root_conn = mysql.connector.connect(**config)  # type: ignore[arg-type]
        root_cursor = root_conn.cursor()
        root_cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        root_cursor.close()
        root_conn.close()

        # Reconnect dengan database attendance_db
        conn = get_db_connection()
        if not conn:
            return False
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                employee_id VARCHAR(50) PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(100) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'employee',
                department VARCHAR(100) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )

        # Drop foreign key lawas yang masih mereferensikan tabel employees eksternal
        cursor.execute(
            """
            SELECT CONSTRAINT_NAME
            FROM information_schema.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = %s
              AND TABLE_NAME = 'users'
              AND CONSTRAINT_TYPE = 'FOREIGN KEY'
            """,
            (DATABASE_NAME,),
        )
        for (fk_name,) in cursor.fetchall():
            try:
                cursor.execute(f"ALTER TABLE users DROP FOREIGN KEY {fk_name}")
                print(f"⚠️ Menghapus foreign key usang pada users: {fk_name}")
            except Error as exc:
                print(f"⚠️ Gagal menghapus FK {fk_name}: {exc}")

        # Tambah kolom yang hilang (jika database lama)
        try:
            if not _column_exists(cursor, "users", "name"):
                cursor.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN name VARCHAR(100) NOT NULL DEFAULT '' AFTER password
                    """
                )
            if not _column_exists(cursor, "users", "department"):
                cursor.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN department VARCHAR(100) DEFAULT '' AFTER role
                    """
                )
        except Error as exc:
            print(f"⚠️ Tidak bisa menambahkan kolom users: {exc}")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id VARCHAR(50) NOT NULL,
                date DATE NOT NULL,
                clock_in TIME,
                clock_out TIME,
                total_hours DECIMAL(5,2) DEFAULT 0,
                is_late BOOLEAN DEFAULT FALSE,
                late_minutes INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_employee_id (employee_id),
                INDEX idx_date (date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )

        # Drop index unik lama jika masih ada
        cursor.execute("SHOW INDEX FROM attendance WHERE Key_name = 'unique_attendance'")
        if cursor.fetchone():
            cursor.execute("ALTER TABLE attendance DROP INDEX unique_attendance")

        # Drop foreign key orphan
        cursor.execute(
            """
            SELECT CONSTRAINT_NAME
            FROM information_schema.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'attendance'
              AND CONSTRAINT_TYPE = 'FOREIGN KEY'
            """,
            (DATABASE_NAME,),
        )
        for (constraint_name,) in cursor.fetchall():
            try:
                cursor.execute(f"ALTER TABLE attendance DROP FOREIGN KEY {constraint_name}")
            except Error:
                pass

        # Seed user default jika belum ada
        cursor.execute("SELECT COUNT(*) FROM users WHERE employee_id = 'USER001'")
        count = cursor.fetchone()
        if not count or count[0] == 0:
            dummy_password = hashlib.sha256("password".encode()).hexdigest()
            cursor.execute(
                """
                INSERT INTO users (employee_id, username, password, name, role, department)
                VALUES ('USER001', 'user', %s, 'User', 'employee', 'IT')
                """,
                (dummy_password,),
            )

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database siap digunakan")
        return True
    except Error as exc:
        print(f"❌ Error initializing database: {exc}")
        return False

