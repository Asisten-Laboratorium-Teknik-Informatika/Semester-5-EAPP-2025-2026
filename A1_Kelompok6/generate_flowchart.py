"""
Script untuk menghasilkan flowchart aplikasi dalam format PDF.
Menggunakan matplotlib untuk menggambar dan reportlab untuk PDF.
"""

from __future__ import annotations

import os
from io import BytesIO

try:
    from matplotlib import pyplot as plt
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
    import numpy as np
except ImportError as e:
    print("⚠️ Library matplotlib/numpy belum terinstall.")
    print("Instal dengan: pip install matplotlib numpy")
    exit(1)

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
except ImportError as e:
    print("⚠️ Library reportlab belum terinstall.")
    print("Instal dengan: pip install reportlab")
    exit(1)


def create_flowchart_login():
    """Membuat flowchart untuk proses Login."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 16))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 20)
    ax.axis('off')
    
    # Judul
    ax.text(5, 19, 'FLOWCHART PROSES LOGIN', 
            ha='center', va='top', fontsize=16, fontweight='bold')
    
    y_pos = 18
    
    # Start
    start_box = FancyBboxPatch((3.5, y_pos-0.5), 3, 0.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor='lightgreen', edgecolor='black', linewidth=1.5)
    ax.add_patch(start_box)
    ax.text(5, y_pos-0.1, 'START', ha='center', va='center', fontsize=12, fontweight='bold')
    y_pos -= 1.5
    
    # Input Username & Password
    input_box = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                               boxstyle="round,pad=0.1", 
                               facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(input_box)
    ax.text(5, y_pos, 'User Input:\nUsername & Password', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Validasi Input
    decision_box = FancyBboxPatch((2.5, y_pos-0.6), 5, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='lightyellow', edgecolor='black', linewidth=1.5)
    ax.add_patch(decision_box)
    ax.text(5, y_pos, 'Validasi Input\n(Kosong?)', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    y_pos -= 2
    
    # Arrow ke validasi
    ax.arrow(5, y_pos+0.6, 0, -0.3, head_width=0.2, head_length=0.1, fc='black', ec='black')
    
    # Branch: Jika kosong
    ax.text(1, y_pos-0.3, 'Ya', ha='right', va='center', fontsize=10, fontweight='bold')
    ax.arrow(2.5, y_pos, -1, 0, head_width=0.15, head_length=0.1, fc='red', ec='red')
    
    # Error Message
    error_box = FancyBboxPatch((0.2, y_pos-1.5), 2.5, 0.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor='lightcoral', edgecolor='black', linewidth=1.5)
    ax.add_patch(error_box)
    ax.text(1.45, y_pos-1.1, 'Tampilkan Error', 
            ha='center', va='center', fontsize=10)
    
    # Branch: Jika tidak kosong
    ax.text(9, y_pos-0.3, 'Tidak', ha='left', va='center', fontsize=10, fontweight='bold')
    ax.arrow(7.5, y_pos, 1, 0, head_width=0.15, head_length=0.1, fc='green', ec='green')
    y_pos -= 2
    
    # Hash Password
    process_box = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box)
    ax.text(5, y_pos, 'Hash Password\n(SHA-256)', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Query Database
    process_box2 = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box2)
    ax.text(5, y_pos, 'Query Database\n(SELECT user WHERE\nusername & password)', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Validasi User
    decision_box2 = FancyBboxPatch((2.5, y_pos-0.6), 5, 1.2, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor='lightyellow', edgecolor='black', linewidth=1.5)
    ax.add_patch(decision_box2)
    ax.text(5, y_pos, 'User Ditemukan?', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    y_pos -= 2
    
    # Branch: Tidak ditemukan
    ax.text(1, y_pos-0.3, 'Tidak', ha='right', va='center', fontsize=10, fontweight='bold')
    ax.arrow(2.5, y_pos, -1, 0, head_width=0.15, head_length=0.1, fc='red', ec='red')
    
    # Error Login
    error_box2 = FancyBboxPatch((0.2, y_pos-1.5), 2.5, 0.8, 
                                boxstyle="round,pad=0.1", 
                                facecolor='lightcoral', edgecolor='black', linewidth=1.5)
    ax.add_patch(error_box2)
    ax.text(1.45, y_pos-1.1, 'Error:\nUsername/Password\nSalah', 
            ha='center', va='center', fontsize=10)
    
    # Branch: Ditemukan
    ax.text(9, y_pos-0.3, 'Ya', ha='left', va='center', fontsize=10, fontweight='bold')
    ax.arrow(7.5, y_pos, 1, 0, head_width=0.15, head_length=0.1, fc='green', ec='green')
    y_pos -= 2
    
    # Set Session
    process_box3 = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box3)
    ax.text(5, y_pos, 'Set Session\n(Backend & Frontend)', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Redirect Dashboard
    process_box4 = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box4)
    ax.text(5, y_pos, 'Redirect ke\nDashboard', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # End
    end_box = FancyBboxPatch((3.5, y_pos-0.5), 3, 0.8, 
                              boxstyle="round,pad=0.1", 
                              facecolor='lightgreen', edgecolor='black', linewidth=1.5)
    ax.add_patch(end_box)
    ax.text(5, y_pos-0.1, 'END', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Arrows
    arrows_y = [18, 16.5, 14.5, 12.5, 10.5, 8.5, 6.5, 4.5, 2.5, 0.5]
    for i in range(len(arrows_y)-1):
        if arrows_y[i] != 14.5 and arrows_y[i] != 6.5:  # Skip decision branches
            ax.arrow(5, arrows_y[i]-0.5, 0, -0.5, head_width=0.2, head_length=0.1, fc='black', ec='black')
    
    plt.tight_layout()
    return fig


def create_flowchart_clock_in():
    """Membuat flowchart untuk proses Clock In."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 18))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 22)
    ax.axis('off')
    
    # Judul
    ax.text(5, 21, 'FLOWCHART PROSES CLOCK IN', 
            ha='center', va='top', fontsize=16, fontweight='bold')
    
    y_pos = 20
    
    # Start
    start_box = FancyBboxPatch((3.5, y_pos-0.5), 3, 0.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor='lightgreen', edgecolor='black', linewidth=1.5)
    ax.add_patch(start_box)
    ax.text(5, y_pos-0.1, 'START', ha='center', va='center', fontsize=12, fontweight='bold')
    y_pos -= 1.5
    
    # User Klik Clock In
    input_box = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                               boxstyle="round,pad=0.1", 
                               facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(input_box)
    ax.text(5, y_pos, 'User Klik\nTombol "Clock In"', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Face Detection
    process_box = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                boxstyle="round,pad=0.1", 
                                facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box)
    ax.text(5, y_pos, 'Face Detection\n(Buka Kamera)', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Deteksi Wajah
    decision_box = FancyBboxPatch((2.5, y_pos-0.6), 5, 1.2, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='lightyellow', edgecolor='black', linewidth=1.5)
    ax.add_patch(decision_box)
    ax.text(5, y_pos, 'Wajah Terdeteksi\n& User Tekan ESC?', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    y_pos -= 2
    
    # Branch: Tidak
    ax.text(1, y_pos-0.3, 'Tidak', ha='right', va='center', fontsize=10, fontweight='bold')
    ax.arrow(2.5, y_pos, -1, 0, head_width=0.15, head_length=0.1, fc='red', ec='red')
    
    # Error Face Detection
    error_box = FancyBboxPatch((0.2, y_pos-1.5), 2.5, 0.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor='lightcoral', edgecolor='black', linewidth=1.5)
    ax.add_patch(error_box)
    ax.text(1.45, y_pos-1.1, 'Error:\nFace Detection\nGagal', 
            ha='center', va='center', fontsize=10)
    
    # Branch: Ya
    ax.text(9, y_pos-0.3, 'Ya', ha='left', va='center', fontsize=10, fontweight='bold')
    ax.arrow(7.5, y_pos, 1, 0, head_width=0.15, head_length=0.1, fc='green', ec='green')
    y_pos -= 2
    
    # Cek Session Terbuka
    decision_box2 = FancyBboxPatch((2.5, y_pos-0.6), 5, 1.2, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor='lightyellow', edgecolor='black', linewidth=1.5)
    ax.add_patch(decision_box2)
    ax.text(5, y_pos, 'Ada Session\nTerbuka?', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    y_pos -= 2
    
    # Branch: Ya (ada session)
    ax.text(1, y_pos-0.3, 'Ya', ha='right', va='center', fontsize=10, fontweight='bold')
    ax.arrow(2.5, y_pos, -1, 0, head_width=0.15, head_length=0.1, fc='red', ec='red')
    
    # Error Session
    error_box2 = FancyBboxPatch((0.2, y_pos-1.5), 2.5, 0.8, 
                                boxstyle="round,pad=0.1", 
                                facecolor='lightcoral', edgecolor='black', linewidth=1.5)
    ax.add_patch(error_box2)
    ax.text(1.45, y_pos-1.1, 'Error:\nSudah Clock In\nBelum Clock Out', 
            ha='center', va='center', fontsize=10)
    
    # Branch: Tidak
    ax.text(9, y_pos-0.3, 'Tidak', ha='left', va='center', fontsize=10, fontweight='bold')
    ax.arrow(7.5, y_pos, 1, 0, head_width=0.15, head_length=0.1, fc='green', ec='green')
    y_pos -= 2
    
    # Ambil Waktu Sekarang
    process_box2 = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box2)
    ax.text(5, y_pos, 'Ambil Waktu\nSekarang', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Validasi Terlambat
    decision_box3 = FancyBboxPatch((2.5, y_pos-0.6), 5, 1.2, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor='lightyellow', edgecolor='black', linewidth=1.5)
    ax.add_patch(decision_box3)
    ax.text(5, y_pos, 'Clock In > 08:30?', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    y_pos -= 2
    
    # Branch: Ya (terlambat)
    ax.text(1, y_pos-0.3, 'Ya', ha='right', va='center', fontsize=10, fontweight='bold')
    ax.arrow(2.5, y_pos, -1, 0, head_width=0.15, head_length=0.1, fc='orange', ec='orange')
    
    # Set Status Terlambat
    process_box3 = FancyBboxPatch((0.2, y_pos-1.5), 2.5, 0.8, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box3)
    ax.text(1.45, y_pos-1.1, 'Set:\nis_late = TRUE\nlate_minutes', 
            ha='center', va='center', fontsize=10)
    
    # Branch: Tidak (on time)
    ax.text(9, y_pos-0.3, 'Tidak', ha='left', va='center', fontsize=10, fontweight='bold')
    ax.arrow(7.5, y_pos, 1, 0, head_width=0.15, head_length=0.1, fc='green', ec='green')
    
    # Set Status On Time
    process_box4 = FancyBboxPatch((7.3, y_pos-1.5), 2.5, 0.8, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box4)
    ax.text(8.55, y_pos-1.1, 'Set:\nis_late = FALSE', 
            ha='center', va='center', fontsize=10)
    
    y_pos -= 2.5
    
    # Insert ke Database
    process_box5 = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box5)
    ax.text(5, y_pos, 'INSERT ke Database\n(attendance table)', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Update UI
    process_box6 = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box6)
    ax.text(5, y_pos, 'Update UI\n(Tombol → "Clock Out"\nStatus → "Clocked In")', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # End
    end_box = FancyBboxPatch((3.5, y_pos-0.5), 3, 0.8, 
                             boxstyle="round,pad=0.1", 
                             facecolor='lightgreen', edgecolor='black', linewidth=1.5)
    ax.add_patch(end_box)
    ax.text(5, y_pos-0.1, 'END', ha='center', va='center', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig


def create_flowchart_clock_out():
    """Membuat flowchart untuk proses Clock Out."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 16))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 20)
    ax.axis('off')
    
    # Judul
    ax.text(5, 19, 'FLOWCHART PROSES CLOCK OUT', 
            ha='center', va='top', fontsize=16, fontweight='bold')
    
    y_pos = 18
    
    # Start
    start_box = FancyBboxPatch((3.5, y_pos-0.5), 3, 0.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor='lightgreen', edgecolor='black', linewidth=1.5)
    ax.add_patch(start_box)
    ax.text(5, y_pos-0.1, 'START', ha='center', va='center', fontsize=12, fontweight='bold')
    y_pos -= 1.5
    
    # User Klik Clock Out
    input_box = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                               boxstyle="round,pad=0.1", 
                               facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(input_box)
    ax.text(5, y_pos, 'User Klik\nTombol "Clock Out"', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Face Detection
    process_box = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box)
    ax.text(5, y_pos, 'Face Detection\n(Buka Kamera)', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Deteksi Wajah
    decision_box = FancyBboxPatch((2.5, y_pos-0.6), 5, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='lightyellow', edgecolor='black', linewidth=1.5)
    ax.add_patch(decision_box)
    ax.text(5, y_pos, 'Wajah Terdeteksi\n& User Tekan ESC?', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    y_pos -= 2
    
    # Branch: Tidak
    ax.text(1, y_pos-0.3, 'Tidak', ha='right', va='center', fontsize=10, fontweight='bold')
    ax.arrow(2.5, y_pos, -1, 0, head_width=0.15, head_length=0.1, fc='red', ec='red')
    
    # Error
    error_box = FancyBboxPatch((0.2, y_pos-1.5), 2.5, 0.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor='lightcoral', edgecolor='black', linewidth=1.5)
    ax.add_patch(error_box)
    ax.text(1.45, y_pos-1.1, 'Error:\nFace Detection\nGagal', 
            ha='center', va='center', fontsize=10)
    
    # Branch: Ya
    ax.text(9, y_pos-0.3, 'Ya', ha='left', va='center', fontsize=10, fontweight='bold')
    ax.arrow(7.5, y_pos, 1, 0, head_width=0.15, head_length=0.1, fc='green', ec='green')
    y_pos -= 2
    
    # Cek Session Terbuka
    decision_box2 = FancyBboxPatch((2.5, y_pos-0.6), 5, 1.2, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='lightyellow', edgecolor='black', linewidth=1.5)
    ax.add_patch(decision_box2)
    ax.text(5, y_pos, 'Ada Session\nTerbuka?', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    y_pos -= 2
    
    # Branch: Tidak
    ax.text(1, y_pos-0.3, 'Tidak', ha='right', va='center', fontsize=10, fontweight='bold')
    ax.arrow(2.5, y_pos, -1, 0, head_width=0.15, head_length=0.1, fc='red', ec='red')
    
    # Error
    error_box2 = FancyBboxPatch((0.2, y_pos-1.5), 2.5, 0.8, 
                                boxstyle="round,pad=0.1", 
                                facecolor='lightcoral', edgecolor='black', linewidth=1.5)
    ax.add_patch(error_box2)
    ax.text(1.45, y_pos-1.1, 'Error:\nBelum Clock In', 
            ha='center', va='center', fontsize=10)
    
    # Branch: Ya
    ax.text(9, y_pos-0.3, 'Ya', ha='left', va='center', fontsize=10, fontweight='bold')
    ax.arrow(7.5, y_pos, 1, 0, head_width=0.15, head_length=0.1, fc='green', ec='green')
    y_pos -= 2
    
    # Ambil Waktu Sekarang
    process_box2 = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box2)
    ax.text(5, y_pos, 'Ambil Waktu\nSekarang', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Hitung Total Jam
    process_box3 = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box3)
    ax.text(5, y_pos, 'Hitung Total Jam\n(clock_out - clock_in)', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Update Database
    process_box4 = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box4)
    ax.text(5, y_pos, 'UPDATE Database\n(SET clock_out, total_hours)', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Update UI
    process_box5 = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box5)
    ax.text(5, y_pos, 'Update UI\n(Tombol → "Clock In"\nStatus → "Clocked Out")', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # End
    end_box = FancyBboxPatch((3.5, y_pos-0.5), 3, 0.8, 
                             boxstyle="round,pad=0.1", 
                             facecolor='lightgreen', edgecolor='black', linewidth=1.5)
    ax.add_patch(end_box)
    ax.text(5, y_pos-0.1, 'END', ha='center', va='center', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig


def create_flowchart_face_detection():
    """Membuat flowchart untuk proses Face Detection."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 14))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 16)
    ax.axis('off')
    
    # Judul
    ax.text(5, 15, 'FLOWCHART PROSES FACE DETECTION', 
            ha='center', va='top', fontsize=16, fontweight='bold')
    
    y_pos = 14
    
    # Start
    start_box = FancyBboxPatch((3.5, y_pos-0.5), 3, 0.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor='lightgreen', edgecolor='black', linewidth=1.5)
    ax.add_patch(start_box)
    ax.text(5, y_pos-0.1, 'START', ha='center', va='center', fontsize=12, fontweight='bold')
    y_pos -= 1.5
    
    # Buka Kamera
    process_box = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                boxstyle="round,pad=0.1", 
                                facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box)
    ax.text(5, y_pos, 'Buka Kamera\n(cv2.VideoCapture(0))', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Cek Kamera Tersedia
    decision_box = FancyBboxPatch((2.5, y_pos-0.6), 5, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='lightyellow', edgecolor='black', linewidth=1.5)
    ax.add_patch(decision_box)
    ax.text(5, y_pos, 'Kamera\nTersedia?', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    y_pos -= 2
    
    # Branch: Tidak
    ax.text(1, y_pos-0.3, 'Tidak', ha='right', va='center', fontsize=10, fontweight='bold')
    ax.arrow(2.5, y_pos, -1, 0, head_width=0.15, head_length=0.1, fc='red', ec='red')
    
    # Error
    error_box = FancyBboxPatch((0.2, y_pos-1.5), 2.5, 0.8, 
                               boxstyle="round,pad=0.1", 
                               facecolor='lightcoral', edgecolor='black', linewidth=1.5)
    ax.add_patch(error_box)
    ax.text(1.45, y_pos-1.1, 'Return Error:\nKamera tidak\ndideteksi', 
            ha='center', va='center', fontsize=10)
    
    # Branch: Ya
    ax.text(9, y_pos-0.3, 'Ya', ha='left', va='center', fontsize=10, fontweight='bold')
    ax.arrow(7.5, y_pos, 1, 0, head_width=0.15, head_length=0.1, fc='green', ec='green')
    y_pos -= 2
    
    # Buka Window
    process_box2 = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box2)
    ax.text(5, y_pos, 'Buka Window\nKamera\n(cv2.imshow)', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Loop Deteksi
    process_box3 = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box3)
    ax.text(5, y_pos, 'Loop: Baca Frame\nDeteksi Wajah\n(Haar Cascade)', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Tampilkan Bounding Box
    process_box4 = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box4)
    ax.text(5, y_pos, 'Jika Wajah Terdeteksi:\nTampilkan Bounding Box\nHijau', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Cek Input Keyboard
    decision_box2 = FancyBboxPatch((2.5, y_pos-0.6), 5, 1.2, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='lightyellow', edgecolor='black', linewidth=1.5)
    ax.add_patch(decision_box2)
    ax.text(5, y_pos, 'User Tekan\nESC?', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    y_pos -= 2
    
    # Branch: Tidak
    ax.text(1, y_pos-0.3, 'Tidak', ha='right', va='center', fontsize=10, fontweight='bold')
    ax.arrow(2.5, y_pos, -1, 0, head_width=0.15, head_length=0.1, fc='blue', ec='blue')
    
    # Kembali ke Loop
    process_box5 = FancyBboxPatch((0.2, y_pos-1.5), 2.5, 0.8, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box5)
    ax.text(1.45, y_pos-1.1, 'Lanjut\nLoop', 
            ha='center', va='center', fontsize=10)
    
    # Arrow kembali ke loop
    ax.arrow(1.45, y_pos-1.5, 0, 3.5, head_width=0.15, head_length=0.1, fc='blue', ec='blue', linestyle='--')
    
    # Branch: Ya
    ax.text(9, y_pos-0.3, 'Ya', ha='left', va='center', fontsize=10, fontweight='bold')
    ax.arrow(7.5, y_pos, 1, 0, head_width=0.15, head_length=0.1, fc='green', ec='green')
    y_pos -= 2
    
    # Cek Wajah Terdeteksi
    decision_box3 = FancyBboxPatch((2.5, y_pos-0.6), 5, 1.2, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='lightyellow', edgecolor='black', linewidth=1.5)
    ax.add_patch(decision_box3)
    ax.text(5, y_pos, 'Wajah\nTerdeteksi?', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    y_pos -= 2
    
    # Branch: Tidak
    ax.text(1, y_pos-0.3, 'Tidak', ha='right', va='center', fontsize=10, fontweight='bold')
    ax.arrow(2.5, y_pos, -1, 0, head_width=0.15, head_length=0.1, fc='red', ec='red')
    
    # Return False
    error_box2 = FancyBboxPatch((0.2, y_pos-1.5), 2.5, 0.8, 
                                boxstyle="round,pad=0.1", 
                                facecolor='lightcoral', edgecolor='black', linewidth=1.5)
    ax.add_patch(error_box2)
    ax.text(1.45, y_pos-1.1, 'Return:\nsuccess = FALSE', 
            ha='center', va='center', fontsize=10)
    
    # Branch: Ya
    ax.text(9, y_pos-0.3, 'Ya', ha='left', va='center', fontsize=10, fontweight='bold')
    ax.arrow(7.5, y_pos, 1, 0, head_width=0.15, head_length=0.1, fc='green', ec='green')
    y_pos -= 2
    
    # Tutup Kamera
    process_box6 = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='lightblue', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box6)
    ax.text(5, y_pos, 'Tutup Kamera\n& Window', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # Return Success
    process_box7 = FancyBboxPatch((2, y_pos-0.6), 6, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='lightgreen', edgecolor='black', linewidth=1.5)
    ax.add_patch(process_box7)
    ax.text(5, y_pos, 'Return:\nsuccess = TRUE', 
            ha='center', va='center', fontsize=11)
    y_pos -= 2
    
    # End
    end_box = FancyBboxPatch((3.5, y_pos-0.5), 3, 0.8, 
                             boxstyle="round,pad=0.1", 
                             facecolor='lightgreen', edgecolor='black', linewidth=1.5)
    ax.add_patch(end_box)
    ax.text(5, y_pos-0.1, 'END', ha='center', va='center', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig


def save_figures_to_pdf():
    """Menyimpan semua flowchart ke dalam satu file PDF."""
    output_file = "FLOWCHART_APLIKASI.pdf"
    
    # Buat buffer untuk menyimpan gambar
    figures = [
        ("Flowchart Proses Login", create_flowchart_login()),
        ("Flowchart Proses Clock In", create_flowchart_clock_in()),
        ("Flowchart Proses Clock Out", create_flowchart_clock_out()),
        ("Flowchart Proses Face Detection", create_flowchart_face_detection()),
    ]
    
    # Buat PDF
    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4
    
    for title, fig in figures:
        # Simpan figure ke buffer
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        
        # Tambahkan halaman baru
        c.showPage()
        
        # Tambahkan judul
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, title)
        
        # Tambahkan gambar
        img = ImageReader(buf)
        img_width, img_height = img.getSize()
        
        # Scale gambar agar muat di halaman
        scale = min((width - 100) / img_width, (height - 100) / img_height)
        scaled_width = img_width * scale
        scaled_height = img_height * scale
        
        # Center gambar
        x = (width - scaled_width) / 2
        y = height - scaled_height - 80
        
        c.drawImage(img, x, y, width=scaled_width, height=scaled_height)
        
        # Tutup figure untuk free memory
        plt.close(fig)
    
    # Simpan PDF
    c.save()
    print(f"Flowchart berhasil disimpan ke: {output_file}")
    print(f"Total halaman: {len(figures)}")


if __name__ == "__main__":
    print("Membuat flowchart...")
    try:
        save_figures_to_pdf()
        print("Selesai! File PDF berhasil dibuat.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

