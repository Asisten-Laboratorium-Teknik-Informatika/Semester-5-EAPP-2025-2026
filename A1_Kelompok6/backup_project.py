"""
Script untuk membuat backup proyek dalam format ZIP.
Menyalin semua file penting kecuali file yang tidak diperlukan.
"""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

# Direktori yang akan diabaikan
IGNORE_DIRS = {
    '__pycache__',
    '.venv',
    'venv',
    'env',
    '.git',
    'node_modules',
    '.pytest_cache',
    '.mypy_cache',
    '__pycache__',
}

# File yang akan diabaikan
IGNORE_FILES = {
    '.pyc',
    '.pyo',
    '.pyd',
    '.DS_Store',
    'Thumbs.db',
    '.gitignore',
    '.env',
}

# Ekstensi yang akan diabaikan (opsional)
IGNORE_EXTENSIONS = {
    '.pyc',
    '.pyo',
    '.pyd',
    '.log',
    '.tmp',
}


def should_ignore(path: Path) -> bool:
    """Cek apakah path harus diabaikan."""
    # Cek direktori
    for part in path.parts:
        if part in IGNORE_DIRS:
            return True
    
    # Cek file
    if path.is_file():
        # Cek ekstensi
        if path.suffix.lower() in IGNORE_EXTENSIONS:
            return True
        # Cek nama file
        if path.name in IGNORE_FILES:
            return True
    
    return False


def create_backup(source_dir: str, output_dir: str = "backups") -> str:
    """
    Membuat backup proyek dalam format ZIP.
    
    Args:
        source_dir: Direktori sumber proyek
        output_dir: Direktori untuk menyimpan backup
    
    Returns:
        Path ke file backup yang dibuat
    """
    source_path = Path(source_dir).resolve()
    
    if not source_path.exists():
        raise ValueError(f"Direktori sumber tidak ditemukan: {source_dir}")
    
    # Buat direktori backup jika belum ada
    backup_dir = Path(output_dir)
    backup_dir.mkdir(exist_ok=True)
    
    # Nama file backup dengan timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_name = source_path.name.replace(" ", "_")
    backup_filename = f"{project_name}_backup_{timestamp}.zip"
    backup_path = backup_dir / backup_filename
    
    print(f"Membuat backup dari: {source_path}")
    print(f"Menuju: {backup_path}")
    print()
    
    # Hitung total file
    total_files = 0
    total_size = 0
    
    # Buat ZIP file
    with ZipFile(backup_path, 'w', ZIP_DEFLATED) as zipf:
        # Walk melalui semua file dan folder
        for root, dirs, files in os.walk(source_path):
            # Filter direktori yang diabaikan
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            root_path = Path(root)
            
            # Skip jika root path harus diabaikan
            if should_ignore(root_path):
                continue
            
            for file in files:
                file_path = root_path / file
                
                # Skip jika file harus diabaikan
                if should_ignore(file_path):
                    continue
                
                # Hitung ukuran file
                try:
                    file_size = file_path.stat().st_size
                    total_size += file_size
                except OSError:
                    continue
                
                # Relatif path untuk ZIP
                arcname = file_path.relative_to(source_path.parent)
                
                try:
                    zipf.write(file_path, arcname)
                    total_files += 1
                    print(f"  [+] {arcname}")
                except Exception as e:
                    print(f"  [!] Error menambahkan {arcname}: {e}")
    
    # Format ukuran
    size_mb = total_size / (1024 * 1024)
    
    print()
    print("=" * 60)
    print(f"Backup berhasil dibuat!")
    print(f"File: {backup_path}")
    print(f"Total file: {total_files}")
    print(f"Ukuran: {size_mb:.2f} MB")
    print("=" * 60)
    
    return str(backup_path)


def main():
    """Fungsi utama."""
    # Dapatkan direktori proyek saat ini
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("SCRIPT BACKUP PROYEK")
    print("=" * 60)
    print()
    
    try:
        backup_file = create_backup(current_dir)
        print()
        print(f"Backup selesai: {backup_file}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

