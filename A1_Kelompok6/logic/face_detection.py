"""
Face detection sederhana via OpenCV.

Mulai sekarang deteksi wajah wajib berhasil (tidak ada fallback otomatis)
agar clock in/out benar-benar divalidasi oleh kamera.
"""

from __future__ import annotations

import os
from contextlib import suppress

import cv2  # type: ignore
import eel  # type: ignore

CASCADE_PATH = os.path.join(
    os.path.dirname(__file__),
    "haarcascade_frontalface_default.xml",
)

# Pastikan file cascade tersedia (fallback ke bawaan cv2 jika ada).
if not os.path.exists(CASCADE_PATH):
    CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"


def _detect_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    classifier = cv2.CascadeClassifier(CASCADE_PATH)
    faces = classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
    return faces


@eel.expose
def detect_face(employee_id):
    """Deteksi wajah user sebelum clock in."""
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return {
                "success": False,
                "message": "Kamera tidak terdeteksi. Pastikan kamera tersambung dan tidak dipakai aplikasi lain.",
                "skipped": False,
            }

        window_name = "Verifikasi Wajah - Tekan Q untuk batal"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)

        detected = False
        max_frames = 150  # ~5 detik
        for _ in range(max_frames):
            ret, frame = cap.read()
            if not ret:
                continue
            faces = _detect_frame(frame)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                if len(faces) > 0:
                    detected = True
                break
            if key in (ord("q"),):
                break

        cap.release()
        with suppress(cv2.error):
            cv2.destroyWindow(window_name)

        if detected:
            return {"success": True, "message": "Wajah terdeteksi", "employee_id": employee_id}
        return {"success": False, "message": "Wajah tidak terdeteksi. Coba lagi."}
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return {"success": False, "message": f"Error saat face detection: {exc}"}

