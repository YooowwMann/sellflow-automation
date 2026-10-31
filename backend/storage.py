import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from backend.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads" / "products"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"]  # WEBP has RIFF header
}

def validate_image_bytes(header: bytes, mime_type: str) -> bool:
    signatures = ALLOWED_MIME_TYPES.get(mime_type)
    if not signatures:
        return False
    for sig in signatures:
        if header.startswith(sig):
            if mime_type == "image/webp":
                # Check for WEBP at byte offset 8
                return len(header) >= 12 and header[8:12] == b"WEBP"
            return True
    return False

async def save_upload_image(file: UploadFile) -> tuple[str, str, str, int]:
    """
    Validasi dan simpan berkas foto produk.
    Mengembalikan: (relative_file_path, original_filename, detected_mime, file_size)
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Berkas tidak memiliki nama."
        )

    # 1. Validasi ekstensi
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format ekstensi '{ext}' tidak diizinkan. Gunakan JPG, PNG, atau WEBP."
        )

    # 2. Baca isi berkas & periksa ukuran
    content = await file.read()
    file_size = len(content)
    max_bytes = settings.max_upload_mb * 1024 * 1024

    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ukuran berkas melebihi batas maksimal {settings.max_upload_mb} MB."
        )

    if file_size < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Berkas gambar terlalu kecil atau kosong."
        )

    # 3. Validasi MIME Type & Signature (Magic Bytes)
    mime_type = file.content_type or "application/octet-stream"
    if mime_type == "image/jpg":
        mime_type = "image/jpeg"

    if mime_type not in ALLOWED_MIME_TYPES or not validate_image_bytes(content[:16], mime_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Isi berkas tidak valid atau bukan gambar yang didukung (JPG, PNG, WEBP)."
        )

    # 4. Buat nama berkas acak (mencegah path traversal dan tabrakan nama)
    secure_filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = UPLOAD_DIR / secure_filename

    # Pastikan dest_path berada di dalam UPLOAD_DIR (anti path traversal)
    if not dest_path.resolve().is_relative_to(UPLOAD_DIR.resolve()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Akses path tidak valid."
        )

    with open(dest_path, "wb") as f:
        f.write(content)

    relative_path = f"/uploads/products/{secure_filename}"
    return relative_path, file.filename, mime_type, file_size

def delete_stored_image(file_path: str) -> None:
    """Hapus berkas foto fisik jika ada."""
    try:
        filename = Path(file_path).name
        target = UPLOAD_DIR / filename
        if target.is_file() and target.resolve().is_relative_to(UPLOAD_DIR.resolve()):
            target.unlink(missing_ok=True)
    except Exception:
        pass
