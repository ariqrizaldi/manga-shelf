# Deploy via Tailscale Funnel (Windows)

Jalur ini tidak membutuhkan kartu kredit, akun cloud, atau domain. Aplikasi
berjalan di PC Windows dan diekspos ke internet lewat Tailscale Funnel.

## Prasyarat

- Python 3.10 atau lebih baru.
- Tailscale terpasang dan sudah login (akun gratis).
- PC menyala dan internet aktif saat aplikasi dipakai.

## Setup pertama

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# edit .env: MANGA_PASSWORD, MANGA_SECRET, MANGA_HTTPS=1
```

Jalankan aplikasi:

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --env-file .env
```

Aktifkan Funnel:

```powershell
& "C:\Program Files\Tailscale\tailscale.exe" funnel --bg 8000
```

URL publik akan muncul, contohnya:

```text
https://nama-pc.nama-tailnet.ts.net
```

Cek status kapan saja:

```powershell
& "C:\Program Files\Tailscale\tailscale.exe" funnel status
```

## Autostart

Shortcut `MangaShelf.lnk` di folder Startup menjalankan
`scripts/run-server.ps1` secara tersembunyi saat login. Script ini:

- menjalankan Uvicorn di `127.0.0.1:8000`;
- menyalakan ulang proses jika berhenti;
- mencegah dua instance berjalan bersamaan.

Funnel dengan `--bg` otomatis aktif lagi setelah reboot atau restart Tailscale.

## Daya

Agar PC tidak sleep saat dicolok:

```powershell
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /change monitor-timeout-ac 10
```

## Backup

```powershell
$env:MANGA_DB = "D:\Ariq\2026\Me!\Projects\manga-shelf\data\manga.db"
.venv\Scripts\python.exe scripts\backup.py
```

Salinan disimpan di `data/backup/` dengan maksimal 14 berkas.

## Menghentikan akses publik

```powershell
& "C:\Program Files\Tailscale\tailscale.exe" funnel --https=443 off
```

## Catatan

- Funnel masih beta dan tunduk pada batas bandwidth yang tidak dipublikasikan.
- URL publik dapat muncul di Certificate Transparency logs. Gunakan kata sandi
  yang kuat; gerbang kata sandi adalah satu-satunya lapisan akses.
- Jika PC mati atau internet rumah putus, URL akan error sampai keduanya hidup
  lagi.
- Jangan bind Uvicorn ke `0.0.0.0`; cukup `127.0.0.1` karena Funnel berjalan di
  mesin yang sama.
