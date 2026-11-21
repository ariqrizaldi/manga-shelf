# MangaShelf

Inventaris koleksi manga per volume. Catat volume mana yang sudah dan belum dimiliki, termasuk koleksi yang bolong-bolong, lalu bawa **Daftar kurang** saat belanja.

Dokumen acuan: [`PRD-Arsip-Koleksi-Manga-v1.3.md`](PRD-Arsip-Koleksi-Manga-v1.3.md) dan [`DESIGN.md`](DESIGN.md).

## Fitur MVP

- CRUD judul + status rilis Ongoing/Tamat dan total volume yang bisa diubah kapan saja.
- Petak volume 1..total: ketuk untuk menandai dimiliki; yang belum dimiliki bergaris putus-putus.
- Input rentang `1-20, 25, 30-44` dengan mode **Tambah**, **Hapus**, dan **Ganti semua** (opsi lanjutan), plus pratinjau.
- Ringkasan otomatis "Belum punya: ..." + tombol salin.
- Tombol **+ Volume baru terbit** untuk judul ongoing.
- Dashboard statistik, pencarian, filter kelengkapan/status baca/rating, sort, tampilan grid/tabel.
- Daftar kurang lintas judul (salin, unduh TXT/CSV).
- Ekspor semua data ke JSON/CSV.
- Cover via URL dengan placeholder inisial; dialog konfirmasi hapus; CSRF dan validasi server.
- Gerbang kata sandi single-user: aktif otomatis bila `MANGA_PASSWORD` diisi, sesi 30 hari, batas 8 percobaan login per 15 menit, dan tombol **Keluar**.

## Menjalankan lokal

Butuh Python 3.10+.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python seed.py          # opsional: 3 contoh dari PRD
uvicorn app.main:app --reload
```

Buka <http://127.0.0.1:8000>. Tanpa `MANGA_PASSWORD`, gerbang login nonaktif
(nyaman untuk pengembangan lokal).

Untuk mencoba gerbang login di lokal:

```powershell
$env:MANGA_PASSWORD = "sandi-lokal-yang-panjang"
uvicorn app.main:app --reload
```

Jangan set `MANGA_HTTPS=1` saat memakai HTTP lokal; cookie `Secure` tidak akan
dikirim dan kamu akan diminta login terus.

Database dibuat otomatis di `data/manga.db` (mode WAL). Untuk memakai lokasi lain:

```powershell
$env:MANGA_DB = "D:\cadangan\manga.db"
```

## Menjalankan dengan Docker

```powershell
Copy-Item .env.example .env
# edit .env: SITE_ADDRESS, MANGA_PASSWORD, MANGA_SECRET
docker compose up -d --build
```

Butuh domain/subdomain yang menunjuk ke mesin tersebut agar Caddy bisa
menerbitkan HTTPS. Panduan lengkap untuk Oracle Cloud Always Free ada di
[`DEPLOY.md`](DEPLOY.md).

## Tes

```powershell
pip install -r requirements-dev.txt
pytest -q
```

Tes mencakup logika rentang (`app/rentang.py`) dan gerbang login
(`tests/test_auth.py`): redirect, CSRF, kata sandi salah, login, dan keluar.

## Struktur

```
app/
├── main.py              # aplikasi, CSRF, gerbang auth, error page
├── auth.py              # sesi cookie, rate limit, middleware login
├── models.py            # Manga, Volume (SQLModel)
├── db.py                # SQLite + PRAGMA foreign_keys/WAL
├── rentang.py           # parser, kompresi, kelengkapan
├── services.py          # view model untuk template
├── routes/              # auth, manga, volume, daftar_kurang, export
├── templates/           # Jinja2 + partial HTMX
└── static/              # token & komponen CSS, HTMX, font lokal
scripts/backup.py        # salinan SQLite aman saat aplikasi hidup
Dockerfile               # image aplikasi
docker-compose.yml       # app + Caddy (HTTPS otomatis)
Caddyfile
```

## Catatan

- Single-user, tanpa akun. Saat di-host publik, isi `MANGA_PASSWORD` agar
  gerbang kata sandi aktif. Aplikasi hanya mendukung satu kata sandi bersama.
- Hanya volume yang dimiliki yang disimpan. Kurang/bolong dihitung dari total volume, jadi judul dengan total belum diketahui tetap didukung.
- Menurunkan total di bawah volume tertinggi yang dimiliki ditolak agar data tidak hilang diam-diam.
- Font Press Start 2P dan IBM Plex Sans di-host lokal di `app/static/fonts`.
- Jalankan satu proses Uvicorn saja; SQLite tidak cocok untuk banyak penulis paralel. Konfigurasi Docker sudah memakai satu worker.
- Cadangkan rutin lewat ekspor JSON atau `scripts/backup.py`; lihat [`DEPLOY.md`](DEPLOY.md).
