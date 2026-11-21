# Deploy MangaShelf di Oracle Cloud Always Free

Panduan ini memasang MangaShelf di satu VM Oracle Cloud yang masuk kuota
**Always Free**, dengan HTTPS otomatis dan gerbang kata sandi. Database SQLite
tetap berupa satu berkas di disk VM.

```
Internet → Caddy (80/443, TLS otomatis) → app FastAPI (8000, internal)
                                              └── SQLite /data/manga.db
```

Perkiraan waktu: 30–45 menit untuk pertama kali.

## 0. Yang perlu disiapkan

- Akun Oracle Cloud. Kartu dipakai untuk verifikasi; selama tetap dalam kuota
  Always Free tidak ada tagihan.
- Repo GitHub **privat** berisi proyek ini.
- SSH key di komputer Windows:

  ```powershell
  ssh-keygen -t ed25519 -C "mangashelf"
  ```

  Jika sudah punya `~/.ssh/id_ed25519.pub`, lewati langkah ini.
- Alamat `sslip.io` gratis: cukup ganti titik pada IP dengan format
  `IP.sslip.io`, misalnya `mangashelf.203.0.113.10.sslip.io`. DNS-nya otomatis
  menunjuk ke IP tersebut, dan Caddy bisa menerbitkan sertifikat Let's Encrypt.

## 1. Buat VM

1. Masuk ke Oracle Cloud Console → **Compute → Instances → Create instance**.
2. Nama: `mangashelf`.
3. Image: **Ubuntu 24.04** (atau versi LTS terbaru).
4. Shape: **Ampere → VM.Standard.A1.Flex**, 1 OCPU / 6 GB. Shape ini termasuk
   Always Free (total kuota **2 OCPU / 12 GB**; 1 OCPU / 6 GB memakai separuh
   kuota dan menyisakan ruang untuk instance kedua).
5. Boot volume: 50 GB (kuota Always Free 200 GB).
6. Centang **Assign a public IPv4 address**.

Always Free hanya berlaku di **home region** tenancy (lihat nama region di
kanan atas konsol). Jika muncul error kapasitas A1, coba availability domain
lain, ulangi beberapa saat lagi, atau pakai **VM.Standard.E2.1.Micro** (AMD,
1/8 OCPU, 1 GB; dua instance gratis) yang cukup untuk aplikasi ini.

> **Risiko reklamasi:** Oracle dapat mengambil kembali instance Always Free
> yang dianggap idle (CPU dan jaringan di bawah 20% selama 7 hari). Karena
> MangaShelf jarang diakses, ini mungkin terjadi. Cadangan rutin dan prosedur
> restore di bagian 9 wajib disiapkan.
7. Tambahkan SSH key publik dari komputer kamu
   (`C:\Users\<nama>\.ssh\id_ed25519.pub`).
8. Setelah VM jadi, catat **public IP**-nya. Sebaiknya buat **Reserved public
   IP** lalu pasang ke VM agar alamat tidak berubah saat VM restart:
   **Networking → IP management → Reserved public IPs → Create**, lalu assign
   ke VNIC instance.

Jika muncul error kapasitas A1 di region tersebut, coba availability domain
lain atau ulangi beberapa saat kemudian.

## 2. Buka port 80 dan 443

**Networking → Virtual Cloud Networks → VCN → Security Lists → Default Security
List → Add Ingress Rules**:

| Source | Protocol | Destination Port |
|---|---|---|
| `0.0.0.0/0` | TCP | `80` |
| `0.0.0.0/0` | TCP | `443` |

Port 22 (SSH) sebaiknya dibatasi ke IP rumah/kantor, bukan `0.0.0.0/0`.
Port 8000 **tidak** perlu dibuka; aplikasi hanya diakses Caddy dari jaringan
internal Docker.

## 3. Masuk dan pasang Docker

```bash
ssh ubuntu@IP_VM

sudo apt-get update
sudo apt-get install -y ca-certificates curl
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
```

Keluar lalu masuk lagi (`exit`, `ssh ubuntu@IP_VM`), kemudian cek:

```bash
docker compose version
```

Jika `ufw` aktif, izinkan port web:

```bash
sudo ufw status
sudo ufw allow 80,443/tcp
```

## 4. Ambil kode dari GitHub

Disarankan memakai **deploy key** (read-only) agar VM tidak menyimpan token
akun GitHub.

Di VM:

```bash
ssh-keygen -t ed25519 -C "mangashelf-vm" -f ~/.ssh/mangashelf_deploy -N ""
cat ~/.ssh/mangashelf_deploy.pub
```

Salin hasilnya ke GitHub → repo → **Settings → Deploy keys → Add deploy key**
(centang *Allow write access* tidak perlu). Lalu:

```bash
nano ~/.ssh/config
```

Isi:

```
Host github.com
  IdentityFile ~/.ssh/mangashelf_deploy
  IdentitiesOnly yes
```

```bash
chmod 600 ~/.ssh/config

sudo mkdir -p /opt/mangashelf
sudo chown $USER:$USER /opt/mangashelf
git clone git@github.com:USER/manga-shelf.git /opt/mangashelf
```

Ganti `USER` dengan username GitHub kamu.

## 5. Isi konfigurasi rahasia

```bash
cd /opt/mangashelf
cp .env.example .env
nano .env
```

Isi ketiga nilai:

```dotenv
SITE_ADDRESS=mangashelf.IP_VM.sslip.io
MANGA_PASSWORD=kata-sandi-panjang-yang-kuat
MANGA_SECRET=hasil-openssl-rand-hex-32
```

Buat `MANGA_SECRET` dengan:

```bash
openssl rand -hex 32
```

Kata sandi sebaiknya 20+ karakter. Gunakan huruf, angka, dan tanda hubung;
hindari `$` dan spasi agar tidak perlu escaping di `.env`.

```bash
chmod 600 .env
```

`MANGA_PASSWORD` wajib. Tanpa variabel ini gerbang login nonaktif dan aplikasi
terbuka untuk siapa saja.

## 6. Jalankan

```bash
cd /opt/mangashelf
docker compose up -d --build
docker compose ps
docker compose logs -f caddy
```

Tunggu sampai Caddy selesai menerbitkan sertifikat (biasanya di bawah satu
menit). Hentikan log dengan `Ctrl+C`, lalu buka:

```
https://mangashelf.IP_VM.sslip.io
```

Kamu akan diarahkan ke halaman **Masuk**. Setelah kata sandi benar, semua fitur
tersedia. Klik **Keluar** di footer untuk mengakhiri sesi.

## 7. Verifikasi cepat

```bash
curl -s https://mangashelf.IP_VM.sslip.io/healthz
# {"status":"ok"}

curl -I https://mangashelf.IP_VM.sslip.io/
# 303 ke /masuk
```

Di browser:

- Kata sandi salah → pesan "Kata sandi salah".
- 8 percobaan salah dalam 15 menit → ditolak sementara.
- Cookie `mangashelf_sesi` memiliki tanda **Secure** dan **HttpOnly**.
- Buka dari HP; tata letak dan FAB tetap berfungsi.

## 8. Update aplikasi

```bash
cd /opt/mangashelf
git pull
docker compose up -d --build
```

Volume `mangashelf_data` tidak tersentuh, jadi data aman.

## 9. Cadangan

### Manual dari aplikasi

**Pengaturan & ekspor → Unduh JSON/CSV**. Ini cadangan logis yang mudah dibaca.

### Salinan berkas database

```bash
cd /opt/mangashelf
docker compose exec -T app python scripts/backup.py
```

Perintah di atas membuat `/data/backup/manga-YYYYMMDD-HHMMSS.db` dan menyimpan
maksimal 14 salinan terakhir. Salin keluar dari VM:

```bash
mkdir -p backups
docker compose cp app:/data/backup/. ./backups
```

Jadwalkan mingguan dengan `crontab -e`:

```cron
15 3 * * 0 cd /opt/mangashelf && docker compose exec -T app python scripts/backup.py && docker compose cp app:/data/backup/. ./backups
```

Salin folder `backups` ke komputer/cloud lain secara berkala. Cadangan yang
hanya berada di VM yang sama bukan cadangan.

### Restore

```bash
cd /opt/mangashelf
docker compose stop app
docker compose cp ./backups/manga-YYYYMMDD-HHMMSS.db app:/data/manga.db
docker compose run --rm --no-deps --user root --entrypoint sh app -c \
  "rm -f /data/manga.db-wal /data/manga.db-shm && chown app:app /data/manga.db"
docker compose start app
```

## 10. Jika ada masalah

| Gejala | Periksa |
|---|---|
| Sertifikat tidak terbit | DNS `sslip.io` harus menunjuk IP VM; port 80 dan 443 terbuka di Security List dan `ufw`; lihat `docker compose logs caddy` |
| Sertifikat tetap gagal | Coba subdomain gratis DuckDNS (`namamu.duckdns.org`) yang diarahkan ke IP VM, lalu ganti `SITE_ADDRESS` |
| Login berhasil tapi kembali ke halaman masuk | Akses harus lewat `https://`; cookie `Secure` tidak dikirim lewat HTTP |
| `502 Bad Gateway` | `docker compose ps` dan `docker compose logs app`; app harus sehat |
| Data hilang setelah redeploy | Pastikan volume `mangashelf_data` terpasang di `/data`; jangan `docker compose down -v` |
| VM Always Free dihentikan Oracle | Instance idle dalam jangka panjang bisa direklamasi; buat VM baru, pasang IP, perbarui `SITE_ADDRESS`, restore cadangan |
| Kapasitas A1 penuh | Coba availability domain lain atau ulangi pembuatan |

Perintah berguna:

```bash
docker compose ps
docker compose logs -f app
docker compose logs -f caddy
docker compose restart app
docker compose down          # aman, volume tetap ada
docker system df             # cek pemakaian disk
```

## 11. Catatan keamanan

- Hanya port 80/443 yang terbuka ke publik; SQLite tidak pernah diekspos.
- Sesi berlaku 30 hari. Mengganti `MANGA_PASSWORD` otomatis membatalkan semua
  sesi lama karena sidik kata sandi ikut ditandatangani di cookie.
- Jangan commit `.env`. Berkas itu sudah masuk `.gitignore`.
- Perbarui image secara berkala:

  ```bash
  docker compose pull
  docker compose build --pull
  docker compose up -d
  ```
