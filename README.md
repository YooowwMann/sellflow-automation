# 🛒 SellFlow Automation

> **Platform Otomasi Katalog Preloved & Publikasi Multi-Kanal Terpadu**  
> Kelola produk preloved (*single-stock*), buat copywriting menarik dengan AI Profesional, dan distribusikan listing ke **Shopee**, **Facebook Group**, serta **Aplikasi Preloved** secara aman dan efisien.

---

## 📌 Tentang Proyek

**SellFlow Automation** dirancang khusus untuk memecahkan masalah umum yang dihadapi oleh penjual barang *preloved* (barang bekas berkualitas, pakaian, sepatu, aksesoris, atau elektronik) yang memiliki stok unik (**hanya 1 unit per barang**).

### Masalah yang Diselesaikan:
1. **Inefisiensi Input Data**: Mengetik ulang judul, spesifikasi, deskripsi, dan mengunggah foto satu per satu ke banyak platform (Shopee, FB Groups, Preloved) memakan waktu lama.
2. **Risiko Pesanan Ganda (*Overselling*)**: Barang laku di satu platform (misalnya Facebook), tetapi lupa dihapus di platform lain (seperti Shopee), sehingga pembeli lain kecewa dan reputasi toko turun.
3. **Risiko Pemblokiran Akun**: Penggunaan bot scraper ilegal atau automasi yang melanggar kebijakan platform (khususnya penutupan Meta Groups API) berisiko membekukan akun penjual.

### Solusi SellFlow:
SellFlow Automation bertindak sebagai **Single Source of Truth** (Pusat Data Tunggal). Cukup input barang dan unggah foto **satu kali**, lalu biarkan AI membuatkan teks penawaran yang dioptimalkan untuk masing-masing platform. Saat barang terjual di salah satu platform, SellFlow secara otomatis menurunkan stok menjadi 0 dan memberikan checklist peringatan untuk menarik postingan dari kanal lainnya.

---

## ✨ Fitur-Fitur Utama

### 1. 📦 Katalog Produk Preloved Lengkap
* Atribut detail barang bekas: **Kategori**, **Merek**, **Ukuran**, **Kondisi Fisik** (*Like New, Sangat Bagus, Bagus, Cukup*), dan **Catatan Minus/Cacat**.
* Galeri multi-foto dengan penataan foto utama (*primary image*).
* Proteksi berkas ketat: validasi ekstensi, batas ukuran berkas (10 MB), dan pemeriksaan **Magic Bytes** (*file signature*) untuk menangkal file berbahaya berkedok gambar.

### 2. 🤖 AI Copywriting Profesional (Dual Engine)
* **Prinsip Kejujuran**: Prompt AI dirancang ketat agar **tidak mengarang** riwayat pemakaian, garansi, kelengkapan, atau klaim kualitas tanpa dasar (*"100% original"*). Jika barang memiliki cacat/minus, AI wajib menyebutkannya dengan sopan dan transparan.
* **Dual Engine Provider**:
  * **Google Gemini AI** (`gemini-2.5-flash`): Hasil tulisan variatif dan adaptif jika API key dikonfigurasi.
  * **Built-in Rule Engine (Bawaan)**: Generator deterministik pintar yang langsung bekerja tanpa biaya token (**Rp 0**) dan tanpa dependensi koneksi luar.
* **Format Disesuaikan per Kanal**:
  * **Shopee**: Judul optimal search keyword (maks. 120 karakter), deskripsi berpoin rapi, dan tagar relevan.
  * **Facebook Group**: Gaya ramah komunitas jual-beli (`[WTS] ...`), harga transparan, dan ajakan chat/PM santai.
  * **Aplikasi Preloved**: Format ringkas yang menonjolkan ukuran dan transparansi kondisi barang.
* **Human-in-the-Loop**: Pengguna dapat meninjau, mengedit draft, menyetujui (*Approve*), dan menyalin teks instan (*Copy to Clipboard*).

### 3. 📢 Publikasi Multi-Kanal yang Sah (*Assisted Posting*)
* **Ban-Safe**: Mengikuti kebijakan terkini Meta (Groups API deprecation) dengan metode **Assisted Posting**. Sistem menyusun paket listing siap pakai (teks teruji, foto, dan tombol pintas ke link grup tujuan).
* Pelacakan status tayang produk di Shopee, Facebook Group, dan Aplikasi Preloved beserta tautan postingan aktif (*external URL*).

### 4. 🔄 Sinkronisasi Stok & Alur Barang Terjual (*Sold Out Flow*)
* Tombol **"Tandai Terjual"** dengan 1 klik ketika ada transaksi yang deal.
* Mencatat kanal penjualan (Facebook, Shopee, Preloved, COD/Offline), harga akhir kesepakatan, dan catatan pembeli.
* Stok otomatis berubah menjadi `0` dan status menjadi `sold`.
* **Cross-Channel Unpublish Checklist**: Sistem mendeteksi otomatis jika barang masih tayang di platform lain dan menampilkan dialog pengingat untuk menghapus/menarik postingan agar tidak terjadi pesanan ganda.

### 5. 📊 Dashboard Analitik & Riwayat Penjualan
* Ringkasan metrik waktu-nyata: Total Produk Aktif, Barang Terbit, Barang Terjual, dan Nilai Inventaris.
* Halaman **Riwayat Penjualan**: Menghitung akumulasi omzet rupiah, analisis kanal paling laris, serta tabel log audit transaksi lengkap (`inventory_events`).

### 6. 🔐 Keamanan Berlapis (Enterprise Hardening)
* Password di-hash menggunakan standar modern **Argon2id** (via `pwdlib`).
* **Proteksi Brute-Force Rate Limiting**: Memblokir percobaan login beruntun (>5 kali gagal dalam 5 menit).
* **W3C Fetch Metadata CSRF Protection**: Menolak request modifikasi state yang berasal dari domain luar (*cross-site*).
* Cookie sesi aman (`HttpOnly`, `SameSite=Lax`, penanganan `Secure`).

---

## 🛠️ Tumpukan Teknologi (Tech Stack)

| Komponen | Teknologi | Keterangan |
| :--- | :--- | :--- |
| **Backend** | Python 3.11–3.13, FastAPI | REST API asynchronous performa tinggi |
| **ORM & Database** | SQLAlchemy 2.0, Alembic | Skema terstruktur dengan version control migration |
| **Database** | SQLite (Dev) / PostgreSQL (Prod) | Transisi mudah cukup via `DATABASE_URL` |
| **Validasi Data** | Pydantic v2 | Validasi skema request dan response yang ketat |
| **Frontend** | HTML5, Vanilla CSS3, Modern JavaScript | Tanpa build tool rumit, ringan, responsif Desktop/Mobile |
| **Pengujian** | Pytest, FastAPI TestClient | 13/13 pengujian otomatis lulus 100% |

---

## 📁 Struktur Direktori

```text
sellflow-automation/
├── backend/
│   ├── ai_service.py     # Modul generator copy AI (Gemini & Built-in Engine)
│   ├── auth.py           # Autentikasi Argon2id, hashing & rate limiting
│   ├── config.py         # Konfigurasi environment & setting aplikasi
│   ├── database.py       # Engine SQLAlchemy & session generator
│   ├── main.py           # Endpoint REST API FastAPI & middleware
│   ├── models.py         # Model ORM (User, Product, Image, Listing, Event)
│   ├── schemas.py        # Skema Pydantic untuk request & response
│   └── storage.py       # Penanganan upload foto aman & validasi magic bytes
├── frontend/
│   ├── index.html        # Antarmuka web Clean Light Dashboard
│   ├── style.css         # Styling antarmuka responsif
│   └── app.js            # Logika UI interaktif (SPA-like dashboard)
├── alembic/              # Berkas migrasi database version-controlled
├── docs/                 # Dokumentasi arsitektur, sejarah & roadmap
│   ├── PROJECT_HISTORY_0_TO_FINISH.md  # Riwayat detail pembangunan 0-Finish
│   ├── ENTERPRISE_SCALING_GUIDE.md     # Cetak biru scaling enterprise & cloud
│   ├── ARCHITECTURE.md                 # Detail arsitektur sistem
│   └── SECURITY_CHECKLIST.md           # Standar keamanan rilis produksi
├── tests/                # Suite pengujian otomatis (Pytest)
├── uploads/              # Direktori penyimpanan foto lokal (diabaikan git)
├── .env.example          # Contoh konfigurasi environment variable
├── Dockerfile            # Kontainerisasi Docker
├── docker-compose.yml    # Orkestrasi Docker lokal
├── requirements.txt      # Daftar dependensi Python
└── pytest.ini            # Konfigurasi environment test
```

---

## 🚀 Panduan Memulai Cepat (Quick Start)

### Persyaratan Sistem:
- Python 3.11 atau lebih baru (kompatibel hingga Python 3.13)
- Windows 10/11, macOS, atau Linux
- PowerShell / Bash

### Langkah Instalasi (Windows PowerShell):

1. **Clone Repositori**:
   ```powershell
   git clone https://github.com/YooowwMann/sellflow-automation.git
   cd sellflow-automation
   ```

2. **Buat & Aktifkan Virtual Environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Instal Dependensi**:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Siapkan Environment**:
   ```powershell
   Copy-Item .env.example .env
   ```

5. **Jalankan Aplikasi**:
   ```powershell
   uvicorn backend.main:app --reload
   ```

6. **Buka Aplikasi di Browser**:
   * Dashboard: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   * Dokumentasi Swagger API: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Kredensial Default Development:
* **Username**: `admin`
* **Password**: `ChangeThisPassword_2026!`
*(Pastikan mengganti kredensial dan `SECRET_KEY` sebelum digunakan di lingkungan produksi).*

---

## 🧪 Menjalankan Pengujian Otomatis

Untuk memverifikasi keandalan API, keamanan upload, sistem autentikasi, dan modul AI, jalankan:

```powershell
pytest -v
```

Semua 13 pengujian (`test_api`, `test_products`, `test_ai`, `test_publish`, `test_inventory`) telah diverifikasi **PASSED (100%)**.

---

## 📚 Dokumentasi Lanjutan

Untuk mempelajari perjalanan pengembangan atau merencanakan ekspansi arsitektur ke tahap cloud enterprise, silakan buka dokumen di folder [`docs/`](file:///C:/Users/Ardi/OneDrive/Dokumen/sellflow-automation/docs):
- 📖 [**PROJECT_HISTORY_0_TO_FINISH.md**](file:///C:/Users/Ardi/OneDrive/Dokumen/sellflow-automation/docs/PROJECT_HISTORY_0_TO_FINISH.md) — Kronologi lengkap transformasi dari 0 sampai MVP selesai.
- 🏢 [**ENTERPRISE_SCALING_GUIDE.md**](file:///C:/Users/Ardi/OneDrive/Dokumen/sellflow-automation/docs/ENTERPRISE_SCALING_GUIDE.md) — Rencana arsitektur multi-tenant, cloud object storage (S3/R2), antrean worker Celery/Redis, integrasi Vision AI, dan Shopee Open Platform API.
- 🛡️ [**SECURITY_CHECKLIST.md**](file:///C:/Users/Ardi/OneDrive/Dokumen/sellflow-automation/docs/SECURITY_CHECKLIST.md) — Standar verifikasi keamanan sebelum deployment produksi.

---

## 📄 Lisensi & Kontribusi
Dikembangkan untuk mendukung UMKM dan penjual online preloved agar dapat beroperasi lebih profesional, aman, dan efisien.
