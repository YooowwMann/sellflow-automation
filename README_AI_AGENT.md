# SELFLOW AUTOMATION — PAKET PROYEK UNTUK AI CODING AGENT

> Baca dokumen ini dan `AGENTS.md` sebelum mengubah kode apa pun.

## Tujuan singkat
SellFlow Automation adalah aplikasi pribadi untuk mengelola satu katalog produk preloved dan menyiapkan/mendistribusikan listing ke:
1. Shopee
2. Facebook Group/komunitas
3. Aplikasi/layanan Preloved yang dimaksud pengguna

Pengguna ingin memasukkan data produk satu kali dari laptop atau HP, lalu menjalankan satu alur publikasi. Otomatisasi penuh hanya boleh dilakukan jika tersedia API/integrasi resmi dan diizinkan oleh platform. Jika tidak, aplikasi harus menyiapkan konten dan meminta tindakan/konfirmasi manual yang sah.

## Keputusan produk yang sudah ditetapkan
- Nama: SellFlow Automation
- Pengguna: satu pemilik/admin pada tahap awal
- Volume: sekitar 1–10 produk per hari
- Perangkat: laptop Windows dan HP Android
- Akses: cloud, dapat diakses dari mana saja
- UI: Clean Light Dashboard, responsif
- Backend: Python + FastAPI
- Frontend: HTML, CSS, JavaScript pada tahap awal
- Database lokal: SQLite untuk development
- Database cloud/production: PostgreSQL
- Browser automation: Playwright hanya untuk alur yang diizinkan dan stabil
- AI: membantu membuat judul, deskripsi, caption, dan variasi konten; pengguna tetap dapat meninjau/mengedit
- Bahasa UI dan dokumentasi: Bahasa Indonesia

## Kondisi saat ini
Tahap 1 adalah fondasi awal: FastAPI, session login sederhana, dashboard awal, model Product/Listing/PublishJob, endpoint health, Dockerfile, dan konfigurasi lokal. Fitur CRUD penuh, upload foto, AI, konektor marketplace, queue worker, dan deployment production belum selesai.

## Cara memulai
1. Baca `AGENTS.md`.
2. Baca `docs/PROJECT_SPEC.md`.
3. Baca `docs/ARCHITECTURE.md`.
4. Baca `docs/PLATFORM_INTEGRATION.md`.
5. Baca `docs/ROADMAP.md` dan `docs/ACCEPTANCE_CRITERIA.md`.
6. Jalankan aplikasi mengikuti `README.md`.
7. Periksa `docs/KNOWN_GAPS.md` sebelum menyatakan fitur siap produksi.

## Aturan penting
Jangan menganggap API Shopee, Facebook Group, atau Preloved sudah tersedia/terhubung. Verifikasi dokumentasi resmi dan izin akses terlebih dahulu. Jangan mengakali CAPTCHA, OTP, MFA, pembatasan akses, atau mekanisme anti-bot. Jangan pernah meminta pengguna mengirim password marketplace ke chat atau menyimpan password mentah.
