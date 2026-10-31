# Architecture — SellFlow

## Prinsip
- Single source of truth: katalog produk internal.
- Adapter per platform: jangan campur logic Shopee/Facebook/Preloved di router.
- Async jobs: proses publikasi/AI yang lama dikerjakan worker.
- Human-in-the-loop: pengguna meninjau konten dan menyelesaikan langkah manual yang diwajibkan.
- Cloud-first: database dan foto harus persisten.

## Komponen target
1. Web UI: HTML/CSS/JS responsive, kemudian dapat menjadi PWA.
2. FastAPI: authentication, product API, AI API, publish orchestration, dashboard.
3. PostgreSQL: produk, foto metadata, listing, jobs, logs, platform account references.
4. Object storage: foto produk (S3-compatible atau layanan setara).
5. Queue: Redis-backed worker atau layanan queue managed; pilih setelah kebutuhan dan biaya dievaluasi.
6. Worker: AI generation, image processing, API calls, status checks.
7. Platform adapters: Shopee adapter, Facebook assisted-post adapter, Preloved adapter.
8. Secrets: environment/secret manager.

## Alur publish
1. User memilih produk dan platform.
2. Backend validasi produk, foto, harga, stok, konten, dan status persetujuan.
3. Backend membuat satu publish job per platform dengan idempotency key.
4. Worker mengambil job.
5. Adapter memeriksa apakah metode resmi tersedia dan credential valid.
6. Jika tersedia: panggil API sesuai dokumentasi, handle rate limits dan response.
7. Jika tidak tersedia: ubah status menjadi `manual_action_required`, siapkan caption/foto/link instruksi.
8. Simpan response reference dan status.
9. Dashboard menampilkan hasil per platform.

## Model data target
- users
- products
- product_images
- platform_accounts
- platform_listings
- publish_jobs
- publish_attempts
- ai_content_drafts
- inventory_events
- audit_logs

## Catatan database
Tahap 1 memakai SQLAlchemy `create_all()` untuk prototipe. Sebelum schema production berubah, tambahkan Alembic migrations. Jangan menjalankan `create_all()` sebagai mekanisme upgrade database production.

## Foto
- Upload melalui backend dengan validasi.
- Simpan metadata di PostgreSQL.
- Simpan file pada object storage persisten.
- Buat thumbnail/resize jika diperlukan.
- Jangan simpan foto pengguna di ephemeral disk cloud.

## API route target
- `/api/auth/*`
- `/api/products`
- `/api/products/{id}/images`
- `/api/ai/listing-drafts`
- `/api/platform-accounts`
- `/api/publish/jobs`
- `/api/publish/jobs/{id}`
- `/api/inventory`
- `/api/dashboard`
- `/api/health`

## Deployment target
- Web/API service di cloud.
- PostgreSQL managed.
- Object storage persisten.
- Worker service terpisah.
- HTTPS custom domain.
- Backup dan monitoring.
