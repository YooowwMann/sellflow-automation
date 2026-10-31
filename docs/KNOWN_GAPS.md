# Known Gaps — Jangan salah mengartikan status

Starter Tahap 1 adalah fondasi prototipe, bukan aplikasi siap produksi.

1. [TERSELESAIKAN DI TAHAP 1] Tabel User ditambahkan dengan password hashing Argon2id.
2. [TERSELESAIKAN DI TAHAP 1] Proteksi CSRF (W3C Fetch Metadata) dan rate limiting login (maksimal 5 percobaan gagal per jendela waktu) telah diimplementasikan.
3. [TERSELESAIKAN DI TAHAP 1] Konfigurasi Alembic migration dan initial schema revision selesai dibuat.
4. [TERSELESAIKAN DI TAHAP 1] Automated tests dengan pytest (7 tes lulus mencakup hashing, health, session, unauthorized access, csrf, rate limit, dan alur produk).
5. [TERSELESAIKAN DI TAHAP 2] CRUD produk lengkap di UI (tambah, edit, hapus, filter, dan cari) telah dibangun.
6. [TERSELESAIKAN DI TAHAP 2] Upload multi-foto dengan validasi keamanan (ekstensi, batas ukuran, dan magic bytes signature) serta galeri foto telah diimplementasikan.
7. [TERSELESAIKAN DI TAHAP 3] Provider AI Copywriter (Google Gemini & Built-in Engine anti-halusinasi), database drafts, approval flow, dan UI copywriting per platform telah aktif.
8. Belum ada job worker/queue (dibutuhkan untuk publikasi latar belakang saat direct API terhubung).
9. [TERSELESAIKAN DI TAHAP 5] Alur Assisted Posting Facebook Group & Paket Publikasi Multi-Kanal (Shopee, FB, Preloved) telah aktif. Koneksi direct API otomatis tetap mematuhi aturan platform resmi.
10. SQLite hanya untuk development; production harus PostgreSQL.
11. Belum ada object storage.
12. Docker Compose starter belum memasang service PostgreSQL; konfigurasi cloud perlu disesuaikan.
13. Cloud deployment belum dilakukan.
14. Belum ada domain/HTTPS/backup/monitoring.

Jangan mengklaim item-item tersebut sudah selesai.
