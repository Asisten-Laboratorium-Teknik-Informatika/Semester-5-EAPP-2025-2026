"""
Utility helpers untuk backend AttendanceHub.

Berisi helper sederhana untuk menyimpan sesi user yang sedang aktif sehingga
backend Eel dapat mengakses employee_id tanpa harus menerimanya dari semua
panggilan frontend.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

# Session sederhana di memori proses.
CURRENT_USER_SESSION: Dict[str, Any] = {}


def set_current_user(user_data: Dict[str, Any]) -> None:
    """Update informasi user yang sedang login."""
    CURRENT_USER_SESSION.clear()
    CURRENT_USER_SESSION.update(user_data)


def get_current_user() -> Optional[Dict[str, Any]]:
    """Ambil user yang sedang aktif (jika ada)."""
    return CURRENT_USER_SESSION or None

