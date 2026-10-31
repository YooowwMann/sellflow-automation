# Platform Integration Notes

Dokumen ini mencatat status yang harus diverifikasi. Status awal semua integrasi adalah **belum terhubung**.

## Shopee
Target metode: Shopee Open Platform/API resmi.
Sebelum implementasi:
- Verifikasi dokumentasi Open Platform terkini.
- Verifikasi kelayakan akun dan app registration.
- Dapatkan approval dan scopes yang benar.
- Implementasikan authorization/token lifecycle sesuai dokumentasi.
- Patuhi rate limits, product category rules, image requirements, dan listing policies.
- Uji di akun yang diizinkan dan satu produk non-kritis.
Jangan mengklaim API sudah aktif sebelum request nyata berhasil.

## Facebook Group
Jangan mengasumsikan Graph API dapat mempublikasikan post ke Groups. Kemampuan Groups API pernah dihentikan Meta; agent wajib memeriksa dokumentasi dan kebijakan Meta terbaru.
Fallback MVP:
- Buat caption yang bisa disalin.
- Sediakan foto yang bisa diunduh/dipilih.
- Simpan URL grup dan instruksi posting.
- Buka halaman grup untuk tindakan pengguna jika sesuai.
- Tandai `manual_action_required`, bukan `published`.
Tidak boleh menggunakan endpoint privat, scraping sesi, akun palsu, atau cara bypass.

## Preloved
Pengguna menyebut aplikasi bernama “Preloved”. Sebelum coding konektor:
- Minta pengguna memastikan nama aplikasi/publisher atau mengirim link listing aplikasi yang tepat.
- Identifikasi website resmi dan alur seller.
- Cari dokumentasi API/partner integration resmi.
- Hubungi dukungan layanan bila perlu.
- Pastikan automasi browser diizinkan oleh syarat layanan.
Jika tidak ada metode sah, gunakan assisted posting.

## Kebijakan umum konektor
- Satu adapter per platform.
- Token terenkripsi saat disimpan (gunakan KMS/secret store bila tersedia).
- OAuth scopes minimum.
- Refresh token dengan aman.
- Idempotency dan retry backoff.
- Hentikan retry pada auth failure, CAPTCHA, OTP, MFA, policy block, atau human verification.
- Catat error code dan pesan yang aman; jangan log token.
- Jangan menandai listing published tanpa response/verification yang dapat dipercaya.
