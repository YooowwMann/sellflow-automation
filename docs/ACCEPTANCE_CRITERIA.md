# Acceptance Criteria

## Tahap 1
- Aplikasi dapat dijalankan pada Windows dengan instruksi README.
- `/api/health` mengembalikan status database.
- Pengguna dapat login dan logout.
- Endpoint dashboard privat memerlukan autentikasi.
- Dashboard menampilkan data ringkasan dari database.
- Tidak ada secret production yang tertanam di source.

## Tahap 2
- Pengguna dapat membuat, membaca, memperbarui, dan mengarsipkan produk.
- Foto tervalidasi dan tampil di halaman detail.
- Data tetap ada setelah server restart.
- Form bekerja pada desktop dan mobile.
- Input invalid menghasilkan pesan yang jelas.

## Tahap 3
- AI hanya memakai data yang disediakan.
- Output draft dapat diedit.
- Tidak ada auto-publish tanpa approval.
- Kegagalan provider AI ditangani.
- Penggunaan/biaya AI dapat dilacak.

## Tahap 5
- Konektor punya bukti autentikasi dan request nyata.
- Status tidak pernah sukses hanya berdasarkan klik atau asumsi.
- Kegagalan satu platform tidak membatalkan status platform lain.
- Assisted-post diberi label manual_action_required.
- Duplicate publish dicegah.

## Production
- Security checklist lulus.
- PostgreSQL migration/backup/restore diuji.
- HTTPS aktif.
- Foto disimpan di persistent object storage.
- Tidak ada default credential.
- Error logs dan monitoring tersedia.
