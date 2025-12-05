"""
Logic package initializer.

Memisahkan modul backend (auth, attendance, database, utils, face detection)
agar bisa di-import oleh main.py maupun file lain.
"""

__all__ = [
    "auth",
    "attendance",
    "database",
    "face_detection",
    "utils",
]

