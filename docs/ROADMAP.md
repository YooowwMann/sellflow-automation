# Roadmap Pembangunan SellFlow

## Tahap 1 — Fondasi (starter tersedia)
- [x] FastAPI app
- [x] Konfigurasi environment
- [x] SQLAlchemy models awal: Product, Listing, PublishJob
- [x] Session login prototipe
- [x] Dashboard awal
- [x] Health endpoint
- [x] Dockerfile
- [x] Hardening auth sebelum production (Argon2id password hashing, login rate limiting, CSRF protection)
- [x] Tests dan test suite (pytest)
- [x] Alembic migrations (konfigurasi & initial migration)

## Tahap 2 — Product Manager
- [x] Product CRUD lengkap (API & UI Dashboard)
- [x] Kategori dan atribut barang (brand, size, condition, defects/minus)
- [x] Multi-image upload (JPG, PNG, WEBP dengan magic bytes signature check)
- [x] Validasi dan preview foto (thumbnail, photo count, modal kelola foto, set primary photo)
- [x] Search, filter, status stok (real-time debounced search, filter kategori & status)
- [x] Archive dan status produk (draft, active, sold, archived)
- [x] Tests (pytest CRUD flow & upload security validation)

## Tahap 3 — AI Listing Generator
- [x] Provider interface untuk AI (dukungan Google Gemini & Built-in Engine anti-halusinasi)
- [x] Prompt aman berbasis fakta produk (tanpa asumsi, wajib sebutkan minus/cacat riil)
- [x] Template per platform (Shopee SEO, Facebook Group WTS, Aplikasi Preloved)
- [x] Draft generation dan editing UI (Modal AI Copywriter dengan live editing per kanal)
- [x] Persetujuan pengguna (fitur Approve sebelum draft dapat dipakai untuk publikasi)
- [x] Biaya/token usage tracking & copy ke clipboard
- [x] Tests hallucination/field-preservation (test suite pytest di tests/test_ai.py)

## Tahap 4 — Cloud foundation
- [ ] PostgreSQL managed
- [ ] Alembic
- [ ] Object storage
- [ ] Production secret management
- [ ] HTTPS dan domain
- [ ] Backup/restore test
- [ ] Monitoring dan rate limits

## Tahap 5 — Platform integration
- [x] Facebook assisted-post workflow (alur paket posting sah, salin teks, unduh foto, tautan grup, dan konfirmasi)
- [x] Shopee & Preloved package workflow (paket persiapan listing terstruktur dan instruksi seller)
- [x] Status pelacakan per platform (not_published, manual_action_required, published)
- [ ] Direct Shopee API OAuth (menunggu persetujuan akun aplikasi Shopee Open Platform resmi)
- [ ] Preloved official partner API (menunggu konfirmasi penyedia layanan resmi)

## Tahap 6 — Automation orchestration
- [ ] Job queue dan worker
- [ ] Publish all selected platforms
- [ ] Per-platform result verification
- [ ] Manual action tasks
- [ ] Retry yang aman
- [ ] Notification center

## Tahap 7 — Inventory sync
- [x] Manual sold flow (modal tandai terjual, input kanal, harga deal, dan catatan pembeli)
- [x] Inventory events (pencatatan audit log transaksi penjualan di database)
- [x] Task menonaktifkan listing kanal lain (modal unpublish checklist untuk cegah pesanan ganda)
- [x] Riwayat Penjualan & Dashboard Omzet (menu Riwayat dengan akumulasi omzet & kanal terlaris)

## Tahap 8 — Mobile/PWA dan production readiness
- [ ] Responsive QA
- [ ] PWA installability
- [ ] Secure remote access
- [ ] Security checklist lulus
- [ ] Load/error tests
- [ ] User acceptance test
