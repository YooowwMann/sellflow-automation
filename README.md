# SellFlow Automation — Tahap 1

Fondasi dashboard, autentikasi administrator, FastAPI, dan database.

## Persyaratan
- Python 3.11 atau lebih baru (disarankan 3.12)
- Windows 10/11
- PowerShell

## Jalankan di Windows
1. Salin `.env.example` menjadi `.env`.
2. Buka PowerShell di folder proyek.
3. Buat virtual environment:
   `py -3.12 -m venv .venv`
4. Aktifkan:
   `.\.venv\Scripts\Activate.ps1`
5. Jika PowerShell memblokir aktivasi, jalankan:
   `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
   lalu aktifkan lagi.
6. Instal:
   `python -m pip install --upgrade pip`
   `pip install -r requirements.txt`
7. Jalankan:
   `uvicorn backend.main:app --reload`
8. Buka `http://127.0.0.1:8000`

Login awal development:
- Username: `admin`
- Password: `ChangeThisPassword_2026!`

Segera ubah password dan SECRET_KEY di `.env`.

## Endpoint
- `GET /api/health` — pemeriksaan aplikasi/database
- `GET /api/session` — status login
- `POST /api/login` — login form
- `POST /api/logout` — logout
- `GET /api/dashboard` — ringkasan (wajib login)
- `GET /api/products` — daftar produk (wajib login)
- `POST /api/products` — membuat produk (wajib login)

Dokumentasi API: `http://127.0.0.1:8000/docs`

## Database
Default lokal menggunakan SQLite. Untuk cloud, gunakan PostgreSQL dan set `DATABASE_URL`, misalnya:
`postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME`

## Catatan keamanan sebelum deployment publik
- Ganti `SECRET_KEY` dengan nilai acak minimal 32 karakter.
- Ganti `ADMIN_USERNAME` dan `ADMIN_PASSWORD`.
- Set `APP_ENV=production` dan `SESSION_HTTPS_ONLY=true`.
- Set `DATABASE_URL` ke PostgreSQL terkelola.
- Jangan commit `.env` ke Git.
- Tambahkan HTTPS, backup database, rate limiting, CSRF protection, dan mekanisme reset password sebelum penggunaan publik/produksi.
- Tahap 1 adalah fondasi awal, belum diaudit keamanan dan belum siap menerima trafik publik tanpa hardening lanjutan.


## Dokumentasi AI Coding Agent
Baca `README_AI_AGENT.md` dan `AGENTS.md` sebelum meminta AI coding agent mengubah proyek. Spesifikasi dan roadmap lengkap berada di folder `docs/`.
