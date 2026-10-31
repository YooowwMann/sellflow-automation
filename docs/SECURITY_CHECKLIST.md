# Security Checklist

## Sebelum development berlanjut
- [x] Tidak ada secret di source control.
- [x] `.env` masuk `.gitignore`.
- [ ] Ganti kredensial default (wajib di production environment).
- [x] Password disimpan dengan Argon2id/bcrypt, bukan plaintext.
- [x] Login rate limiting.
- [x] CSRF protection untuk cookie session (W3C Fetch Metadata).
- [x] Cookie HttpOnly, Secure (production), SameSite.
- [x] Session expiry dan logout invalidation.
- [x] Authorization pada setiap endpoint privat.

## Upload
- [x] Batas ukuran file (maksimal 10 MB per foto).
- [x] Validasi MIME dan signature file (magic bytes checking untuk JPG, PNG, WEBP).
- [x] Nama file acak (UUID hex anti-collision).
- [x] Cegah path traversal (verifikasi path containment).
- [x] Batasi jumlah foto per produk (maksimal 10 foto).
- [ ] Storage privat atau signed URL (disiapkan saat integrasi S3 cloud storage).
- [x] Hindari file executable (ekstensi dan MIME non-gambar ditolak).

## Cloud
- [ ] HTTPS.
- [ ] Secret manager/env secrets.
- [ ] PostgreSQL tidak terbuka ke publik tanpa alasan.
- [ ] Backup otomatis.
- [ ] Restore diuji.
- [ ] Logging tidak menyimpan token/password.
- [ ] Rate limit dan monitoring.
- [ ] Dependency scanning dan update berkala.

## Platform
- [ ] OAuth scopes minimum.
- [ ] Token terenkripsi.
- [ ] Patuhi terms/rate limits.
- [ ] CAPTCHA/OTP/MFA selalu diselesaikan manusia.
- [ ] Tidak menggunakan endpoint privat atau credential hasil ekstraksi.
- [ ] Publikasi hanya setelah approval pengguna atau aturan auto-approval eksplisit.

Status: Tahap 1 belum memenuhi seluruh checklist production.
