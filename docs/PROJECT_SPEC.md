# Project Specification — SellFlow Automation

## 1. Ringkasan
SellFlow adalah aplikasi pribadi untuk mengelola katalog barang preloved dan membantu distribusi listing ke beberapa kanal penjualan dari satu dashboard.

## 2. Masalah pengguna
Pengguna menjual barang melalui Shopee, Facebook Group/komunitas, dan aplikasi Preloved. Menginput ulang judul, deskripsi, harga, serta foto pada tiga kanal memakan waktu dan membuat pengguna enggan mengunggah produk secara rutin.

## 3. Tujuan
- Satu kali input data produk.
- Simpan katalog terpusat.
- Buat draft judul/deskripsi/caption dengan AI.
- Distribusikan ke kanal yang diizinkan.
- Sediakan assisted posting bila direct publishing tidak tersedia.
- Pantau status per kanal.
- Kurangi risiko stok ganda/produk tetap tayang setelah terjual.
- Bisa digunakan melalui laptop Windows dan HP Android.

## 4. Bukan tujuan
- Mengirim spam atau posting massal tanpa kontrol.
- Menghindari CAPTCHA, OTP, MFA, rate limit, atau proteksi platform.
- Menjamin semua platform mendukung auto-publish.
- Mengelola pembayaran atau checkout pembeli pada tahap awal.
- Menyimpan password marketplace pengguna.

## 5. Pengguna dan peran
MVP: satu administrator/pemilik. Rancangan multi-user dapat dipertimbangkan kemudian, tetapi jangan menambah kompleksitas sebelum dibutuhkan.

## 6. Kebutuhan fungsional
### F1 — Authentication
- Login/logout administrator.
- Password di-hash.
- Session aman dan dapat dicabut.
- Rate limit login dan proteksi CSRF.

### F2 — Product Manager
- Create, read, update, archive/delete product.
- Nama, kategori, brand (opsional), harga, kondisi, deskripsi, ukuran/varian, stok, catatan cacat/kelengkapan.
- Upload beberapa foto.
- Preview foto.
- Validasi input dan file.

### F3 — AI Listing Generator
- Generate title, description, caption, hashtags bila diizinkan.
- Template per platform.
- Hasil dapat diedit dan disimpan sebagai draft.
- Pengguna menyetujui sebelum publish.
- Tidak mengarang detail produk.

### F4 — Multi-Platform Publisher
- Satu publish request dapat membuat job untuk beberapa platform.
- Setiap platform memiliki status independen.
- Idempotency key untuk mencegah duplikasi.
- Retry terbatas untuk error sementara.
- Manual action state untuk assisted posting.
- Simpan external listing ID/URL jika platform mengembalikannya.

### F5 — Inventory
- Stok pusat.
- Status available, reserved (opsional), sold, archived.
- Konfirmasi penjualan manual pada MVP.
- Jika barang sold, buat task untuk menonaktifkan listing di kanal lain; hanya otomatis jika API dan izin mendukung.

### F6 — Dashboard & Logs
- Total produk, draft, aktif, sold.
- Status integrasi per platform.
- Riwayat publish jobs dan pesan error yang aman.
- Filter dan pencarian produk.

### F7 — Mobile access
- Responsive web/PWA.
- Dashboard dapat dipakai pada layar HP.
- Cloud deployment dengan HTTPS.

## 7. Non-functional requirements
- Bahasa UI Indonesia.
- Clean light design.
- Responsif untuk mobile dan desktop.
- API tervalidasi dengan Pydantic.
- PostgreSQL production.
- File storage cloud persisten.
- Logging tanpa secret.
- Backup dan restore.
- Tests untuk alur kritis.
- Observability minimum: health endpoint dan error logs.

## 8. Data produk minimum
- id
- name
- category
- brand (nullable)
- price
- condition
- size_or_variant
- stock
- description
- defects_and_completeness
- status
- created_at / updated_at

## 9. Status listing yang disarankan
- draft
- ready_for_review
- queued
- publishing
- published
- manual_action_required
- failed
- removed
- sold

Jangan menggunakan satu status global untuk menggantikan status tiga platform yang bisa berbeda.

## 10. KPI MVP
- Membuat satu produk dan menyimpan foto tanpa error.
- Generate draft konten dari data yang diberikan.
- Pengguna dapat mengedit dan menyetujui draft.
- Sistem membuat job terpisah untuk kanal yang dipilih.
- Status per kanal dapat dilihat.
- Tidak ada klaim publikasi sukses tanpa bukti.
- Alur manual tetap tersedia jika integrasi tidak didukung.
