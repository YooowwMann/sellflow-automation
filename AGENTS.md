# AGENTS.md — ATURAN WAJIB AI CODING AGENT

Dokumen ini adalah instruksi utama untuk AI coding agent yang mengerjakan SellFlow Automation. Jika instruksi lain bertentangan, prioritaskan keamanan, aturan platform, dan instruksi eksplisit pemilik proyek.

## 1. Misi dan pemahaman produk
Bangun aplikasi bernama **SellFlow Automation** untuk membantu satu penjual mengelola produk preloved dan mempersiapkan/menerbitkan listing ke Shopee, Facebook Group, dan Preloved.

Alur inti yang dituju:
1. Pengguna login ke dashboard.
2. Pengguna membuat satu data produk dan mengunggah beberapa foto.
3. Sistem menyimpan katalog produk sebagai sumber data utama.
4. AI membuat saran judul, deskripsi, dan caption per platform.
5. Pengguna meninjau dan mengedit konten.
6. Pengguna memilih platform tujuan.
7. Sistem menjalankan konektor yang sah, memverifikasi hasil, dan menyimpan status tiap platform.
8. Jika publikasi otomatis tidak diizinkan/tersedia, sistem membuat paket posting dan mengarahkan pengguna ke langkah manual.
9. Stok dan status produk dapat diperbarui ketika barang terjual.

Jangan mengubah tujuan produk menjadi bot spam, scraper agresif, atau alat untuk menghindari kebijakan platform.

## 2. Profil pengguna dan keputusan yang tidak boleh diubah tanpa persetujuan
- Pengguna memakai Windows laptop dan Android.
- Aplikasi harus responsif dan dapat diakses melalui internet.
- UI memakai gaya Clean Light Dashboard.
- Pengguna menginginkan AI untuk membantu copywriting produk.
- Target volume awal 1–10 produk per hari.
- Biaya diusahakan serendah mungkin; jelaskan biaya hosting, database, AI, dan storage sebelum menambah layanan berbayar.
- Bahasa utama: Indonesia.
- Nama proyek: SellFlow Automation.

## 3. Teknologi dan arsitektur
- Backend: Python + FastAPI.
- ORM: SQLAlchemy.
- Validasi: Pydantic.
- Database development: SQLite.
- Database production: PostgreSQL.
- Frontend awal: HTML, CSS, JavaScript; pertahankan sederhana sampai ada alasan kuat untuk migrasi.
- File foto: object storage yang sesuai untuk cloud; jangan menyimpan file upload permanen hanya di filesystem ephemeral server.
- Background jobs: gunakan queue/worker untuk publikasi dan proses AI yang memerlukan waktu; jangan menjalankan pekerjaan panjang di request web.
- Browser automation: Playwright hanya jika diizinkan oleh ketentuan platform dan tidak ada API resmi yang sesuai.
- Deployment: Docker-compatible cloud service; rahasiakan seluruh credentials.

Jangan menambahkan framework, database, layanan cloud, atau dependency besar tanpa menjelaskan alasan dan konsekuensi biaya/operasional.

## 4. Aturan integrasi platform — sangat penting
### Shopee
- Prioritaskan Shopee Open Platform/API resmi.
- Verifikasi dokumentasi terkini, eligibility akun, proses app registration, scopes, approval, token lifecycle, rate limits, dan endpoint yang benar sebelum implementasi.
- Jangan mengklaim koneksi berhasil sebelum proses OAuth/authorization dan panggilan API nyata berhasil diuji.
- Jangan melakukan scraping atau browser automation untuk menghindari batasan API.

### Facebook Group/komunitas
- Jangan mengasumsikan Graph API dapat mempublikasikan post ke Facebook Groups.
- Meta menghentikan Groups API; verifikasi kebijakan dan kemampuan terkini dari dokumentasi resmi sebelum setiap perubahan desain.
- Jika direct group publishing tidak tersedia/diizinkan, implementasikan workflow assisted posting: siapkan caption, foto, checklist, dan tautan grup; pengguna menyelesaikan publikasi sendiri.
- Jangan menggunakan akun palsu, cookie hasil curian, endpoint privat, atau automasi yang melanggar aturan Meta.

### Preloved
- Nama yang dimaksud pengguna adalah aplikasi bernama “Preloved”; jangan menganggap nama domain/layanan tertentu sudah terkonfirmasi sebagai target yang benar.
- Konfirmasi identitas aplikasi, website resmi, metode login, dan mekanisme seller bersama pengguna.
- Cari dokumentasi API/partner integration resmi atau minta konfirmasi dukungan Preloved.
- Jangan mengasumsikan API publik tersedia.
- Browser automation hanya boleh digunakan jika syarat layanan mengizinkan dan alurnya tidak melewati CAPTCHA, OTP, MFA, rate limits, atau kontrol keamanan.
- Jika tidak ada jalur yang diizinkan, sediakan paket posting manual.

## 5. Keamanan wajib
- Jangan pernah hardcode API keys, session secrets, passwords, OAuth tokens, atau database credentials.
- Semua secret berasal dari environment variables/secret manager.
- Jangan commit `.env`, database produksi, foto pengguna, token, atau file log sensitif.
- Password harus di-hash dengan algoritma password hashing yang sesuai (mis. Argon2id atau bcrypt); jangan menyimpan password mentah.
- Gunakan HTTPS di production, cookie `Secure`, `HttpOnly`, dan `SameSite` yang sesuai.
- Terapkan CSRF protection untuk session-authenticated state-changing requests.
- Tambahkan rate limiting untuk login dan endpoint sensitif.
- Validasi ukuran, MIME type, ekstensi, dan isi file foto; buat nama file acak; cegah path traversal.
- Terapkan otorisasi pada semua endpoint data; jangan hanya menyembunyikan tombol di frontend.
- Jangan menampilkan stack trace, token, password, atau detail internal ke pengguna.
- Gunakan prinsip least privilege pada OAuth scopes.
- Jangan mencatat secret atau data pribadi ke log.
- Tambahkan backup database dan uji pemulihan sebelum production.
- Production belum boleh dinyatakan aman sebelum checklist `docs/SECURITY_CHECKLIST.md` terpenuhi.

## 6. Aturan AI copywriting
- AI hanya membuat saran konten; pengguna dapat mengedit dan menyetujui.
- Jangan mengarang kondisi barang, ukuran, merek, kelengkapan, garansi, keaslian, cacat, atau riwayat pemakaian.
- Gunakan hanya data produk dan keterangan pengguna.
- Jika informasi penting kosong, tanyakan atau tandai sebagai belum diketahui; jangan menebak.
- Hindari klaim “original”, “100% authentic”, “like new”, atau klaim kualitas lain tanpa dasar yang diberikan pengguna.
- Sediakan output berbeda sesuai batas karakter/format platform setelah batas tersebut diverifikasi.
- Jangan memasukkan nomor telepon, tautan eksternal, atau ajakan transaksi yang dilarang oleh kebijakan platform.
- Simpan versi draft dan versi yang disetujui; jangan mempublikasikan output AI tanpa persetujuan pengguna kecuali pengguna secara eksplisit mengaktifkan kebijakan auto-approve untuk template tertentu.

## 7. Kualitas kode
- Gunakan struktur modular dan nama fungsi/variabel yang jelas.
- Tambahkan type hints pada fungsi penting.
- Pisahkan router, schema, model, service, dan konfigurasi.
- Gunakan database migrations (Alembic) sebelum schema production berkembang; jangan mengandalkan `create_all()` untuk upgrade production.
- Tangani error secara eksplisit dan tampilkan pesan yang dapat ditindaklanjuti.
- Jangan menelan exception secara diam-diam.
- Hindari duplikasi logic; gunakan service layer.
- Jangan menambahkan TODO tanpa menjelaskan pemilik/next action.
- Jangan menghapus fitur yang ada tanpa alasan dan tes.
- Jangan mengubah kontrak API tanpa memperbarui dokumentasi dan frontend.
- Jangan membuat data contoh seolah-olah data penjualan nyata.

## 8. Aturan pengerjaan setiap tugas
Sebelum coding:
1. Baca instruksi ini dan dokumen proyek terkait.
2. Periksa struktur file dan kode yang sudah ada.
3. Identifikasi dampak perubahan pada API, database, frontend, security, dan platform policies.
4. Buat rencana singkat dan daftar file yang akan berubah.
5. Jika ada ketidakpastian yang memengaruhi keputusan produk/akses platform, ajukan satu pertanyaan yang paling penting; jangan mengarang.

Saat coding:
1. Kerjakan perubahan terkecil yang memenuhi tujuan.
2. Pertahankan kompatibilitas.
3. Tambahkan validasi dan error handling.
4. Jangan menambahkan secret atau akun pribadi ke repo.
5. Jangan melakukan publish, transaksi, penghapusan data, atau tindakan eksternal tanpa otorisasi eksplisit.

Setelah coding:
1. Jalankan formatter/linter/test yang tersedia.
2. Tambahkan atau perbarui tests.
3. Uji endpoint dan alur UI yang berubah.
4. Periksa diff untuk secret, file besar, dan perubahan tak terkait.
5. Perbarui README/docs/roadmap.
6. Laporkan: file yang berubah, fitur selesai, perintah tes, hasil tes, risiko, dan pekerjaan yang belum selesai.
7. Jangan menyebut “berhasil” jika belum diuji.

## 9. Definition of Done
Sebuah fitur baru hanya dianggap selesai jika:
- Kebutuhan pengguna dipenuhi.
- Validasi backend ada.
- Error state ditangani.
- UI responsif dan usable di laptop/HP.
- Security dan platform rules diperiksa.
- Tests yang relevan lulus.
- Dokumentasi diperbarui.
- Tidak ada credential/secret dalam source.
- Status integrasi hanya “connected/published” setelah ada bukti respons nyata dari platform.

## 10. Komunikasi
- Jelaskan dengan Bahasa Indonesia yang jelas dan bertahap.
- Jangan mengasumsikan pengguna sudah memahami istilah teknis.
- Berikan perintah PowerShell yang bisa langsung disalin untuk Windows.
- Bedakan dengan jelas antara fitur yang sudah dibuat, mockup, simulasi, dan integrasi nyata.
- Jika layanan berbayar dibutuhkan, jelaskan sebelum memilih atau mengaktifkannya.
