"""
Modul autentikasi user (login/register) untuk AttendanceHub.
"""

from __future__ import annotations

import hashlib
from typing import Optional

import eel  # type: ignore

from logic.database import get_db_connection
from logic.utils import set_current_user


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_employee_id() -> Optional[str]:
    """Generate employee_id berurutan USER001, USER002, dst."""
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT employee_id FROM users ORDER BY employee_id DESC LIMIT 1")
        row = cursor.fetchone()
        if row and row[0].startswith("USER") and row[0][4:].isdigit():
            next_id = int(row[0][4:]) + 1
        else:
            next_id = 1
        new_id = f"USER{next_id:03d}"
        cursor.close()
        conn.close()
        return new_id
    except Exception as exc:  # pragma: no cover - hanya logging
        print(f"Error generating employee ID: {exc}")
        cursor.close()
        conn.close()
        return None


@eel.expose
def login_user(username: str, password: str):
    try:
        if not username or not password:
            return {"success": False, "message": "Username dan password harus diisi"}

        conn = get_db_connection()
        if not conn:
            return {"success": False, "message": "Tidak dapat terhubung ke database"}

        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (username, hash_password(password)),
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return {"success": False, "message": "Username atau password salah"}

        user_data = {
            "employee_id": user["employee_id"],
            "username": user["username"],
            "name": user.get("name") or user["username"],
            "role": user.get("role", "employee"),
            "department": user.get("department", ""),
        }
        set_current_user(user_data)
        return {"success": True, "message": "Login berhasil", "user": user_data}
    except Exception as exc:  # pragma: no cover
        import traceback

        traceback.print_exc()
        return {"success": False, "message": f"Error saat login: {exc}"}


@eel.expose
def register_user(employee_id, username, password, role, full_name, department=""):
    try:
        if not username or not password or not full_name or not role:
            return {
                "success": False,
                "message": "Username, password, role, dan nama lengkap harus diisi",
            }
        if len(password) < 6:
            return {"success": False, "message": "Password harus minimal 6 karakter"}

        conn = get_db_connection()
        if not conn:
            return {"success": False, "message": "Tidak dapat terhubung ke database"}

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"success": False, "message": "Username sudah digunakan"}

        if not employee_id:
            employee_id = generate_employee_id()
        if not employee_id:
            cursor.close()
            conn.close()
            return {"success": False, "message": "Gagal membuat employee ID"}

        cursor.execute("SELECT 1 FROM users WHERE employee_id = %s", (employee_id,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {
                "success": False,
                "message": f"Employee ID {employee_id} sudah terdaftar",
            }

        cursor.execute(
            """
            INSERT INTO users (employee_id, username, password, name, role, department)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (employee_id, username, hash_password(password), full_name, role, department),
        )
        conn.commit()
        cursor.close()
        conn.close()

        user_data = {
            "employee_id": employee_id,
            "username": username,
            "name": full_name,
            "role": role,
            "department": department or "",
        }
        set_current_user(user_data)
        return {"success": True, "message": "Registrasi berhasil", "user": user_data}
    except Exception as exc:  # pragma: no cover
        import traceback

        traceback.print_exc()
        return {"success": False, "message": f"Error saat registrasi: {exc}"}


@eel.expose
def check_username_available(username: str):
    try:
        if not username or len(username) < 3:
            return {"available": False, "message": "Username harus minimal 3 karakter"}

        conn = get_db_connection()
        if not conn:
            return {"available": False, "message": "Tidak dapat terhubung ke database"}

        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
        exists = cursor.fetchone()
        cursor.close()
        conn.close()
        if exists:
            return {"available": False, "message": "Username sudah terdaftar"}
        return {"available": True, "message": "Username tersedia"}
    except Exception as exc:  # pragma: no cover
        import traceback

        traceback.print_exc()
        return {"available": False, "message": f"Error checking username: {exc}"}

