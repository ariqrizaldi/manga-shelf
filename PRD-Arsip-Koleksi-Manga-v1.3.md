# PRD — Inventaris Koleksi Manga Web

> Product Requirements Document (Dokumen Kebutuhan Produk)
> Versi: 1.3 · Tanggal: 20 November 2026 · Status: Siap Review
> Dokumen pendamping: `DESIGN.md` (panduan visual)

---

## 1. Informasi Dokumen

| Field | Nilai |
|---|---|
| Nama Produk | **MangaShelf** (nama sementara) |
| Versi Dokumen | 1.3 |
| Tanggal Dibuat | 20 November 2026 |
| Penulis | Ariq |
| Status | Siap review |
| Stakeholder | Pemilik koleksi (single user / personal) |

**Riwayat Perubahan**

| Versi | Tanggal | Perubahan |
|---|---|---|
| 1.0 | 20-11-2026 | Draft awal PRD |
| 1.1 | 20-11-2026 | Stack ditetapkan (FastAPI + Jinja2 + HTMX + SQLite), arah desain retro Nintendo abu tua, perapian scope |
| 1.2 | 20-11-2026 | **Fokus berubah ke inventaris per volume**: koleksi bisa bolong-bolong (mis. punya 32 dari 64). Field **genre** dan **lokasi** dihapus. Tracking per volume naik dari Fase 2 menjadi **inti MVP**. Ditambah input rentang, daftar kurang (daftar belanja), dan status kelengkapan |
| 1.3 | 20-11-2026 | **Dukungan judul ongoing**: field `status_rilis` (Ongoing/Tamat), total volume bisa diubah kapan saja, tombol "+ Volume baru terbit". Input rentang punya mode **Tambah / Hapus / Ganti semua** (default Tambah). Status kelengkapan baru "Terbaru" untuk judul ongoing yang sudah up to date |

**Ringkasan perubahan dari v1.2**

| # | Perubahan | Alasan |
|---|---|---|
| 1 | Tambah field `status_rilis` (`ongoing` / `tamat`) | Judul yang masih terbit punya total volume yang terus bertambah |
| 2 | Total volume bisa diubah langsung di halaman detail (tombol - / +), petak ikut bertambah/berkurang | Jumlah petak harus selalu mengikuti total |
| 3 | Tombol "+ Volume baru terbit" (khusus ongoing); volume baru **tidak** otomatis dimiliki | Volume baru langsung muncul sebagai kekurangan |
| 4 | Input rentang: mode **Tambah** (default), **Hapus**, **Ganti semua** | Mencegah catatan lama tertimpa tanpa sengaja |
| 5 | Status kelengkapan baru **Terbaru**; judul ongoing yang up to date tidak dihitung "belum lengkap" | Tanpa ini, judul ongoing selalu terlihat kurang setiap ada volume baru |
| 6 | Menurunkan total di bawah volume yang dimiliki **ditolak**, bukan sekadar diperingatkan | Mencegah data hilang diam-diam |
| 7 | Nomor di atas total ditolak ("Naikkan total dulu") | Konsistensi petak dan data |
| 8 | F-17 baru (Status Rilis dan Volume Baru Terbit); ID Should/Could-Have bergeser +1 | Fitur baru masuk MVP |

**Ringkasan perubahan dari v1.1 ke v1.2**

| # | Perubahan | Alasan |
|---|---|---|
| 1 | Hapus field `genre` beserta filternya | Tidak dibutuhkan untuk inventaris |
| 2 | Hapus field `lokasi` beserta F-12 | Tidak dibutuhkan |
| 3 | Tracking per volume (tabel `volume`) jadi MVP | Koleksi bisa bolong; angka "32/64" saja tidak menjawab "volume mana yang belum punya" |
| 4 | Kolom `volume_dimiliki` dihapus dari `manga`; dihitung dari tabel `volume` | Mencegah angka tidak sinkron dengan daftar volume |
| 5 | Tambah input rentang, petak volume, ringkasan "Belum punya: ...", halaman Daftar kurang | Mempercepat input dan memudahkan cek saat di toko |
| 6 | Status kelengkapan (lengkap / ada bolong / belum sampai akhir / kosong) dan filternya | Menjawab "bagian mana yang belum punya" |
| 7 | `status_baca` jadi opsional (default "belum") | Fokus aplikasi adalah inventaris, bukan pelacak baca |
| 8 | Kartu statistik diganti: Total judul, Volume dimiliki, Volume kurang, Judul belum lengkap | Selaras dengan tujuan baru |

---

## 2. Ringkasan Eksekutif

MangaShelf adalah aplikasi web personal untuk **menginventaris koleksi manga per volume**. Untuk setiap judul, pengguna bisa mencatat nomor volume mana yang dimiliki dan mana yang belum, termasuk koleksi yang bolong-bolong (mis. punya 32 dari 64 volume, tersebar tidak berurutan). Aplikasi lalu menampilkan hasilnya sebagai daftar yang mudah dibaca, seperti **"Belum punya: 21-24, 31-40, 45-64"**, dan menggabungkan semua kekurangan menjadi satu **Daftar kurang** yang bisa dibawa saat belanja. Judul yang masih **ongoing** juga didukung: total volume bisa ditambah setiap kali ada volume baru terbit.

Fokus utama adalah **kesederhanaan**: satu pengguna, tanpa login di MVP, bisa dijalankan lokal maupun di-host gratis. Tampilannya mengusung gaya **minimalis retro Nintendo dengan warna abu tua**.

---

## 3. Masalah & Peluang

### Masalah
- Koleksi tersebar (rak, karton, folder digital) dan tidak ada catatan **volume nomor berapa saja** yang sudah dimiliki.
- Koleksi sering bolong: beli tidak berurutan, ada volume yang hilang, dipinjam, atau belum ketemu. Angka "32 dari 64" tidak memberi tahu mana yang kurang.
- Saat di toko atau marketplace, sulit memastikan volume yang akan dibeli belum dimiliki, sehingga terjadi pembelian ganda.
- Catatan di notes/kertas mudah hilang dan tidak bisa dicari.

### Peluang
- Satu tempat yang jelas menjawab: "Judul ini, volume berapa saja yang belum saya punya?"
- Daftar kurang gabungan lintas judul sebagai daftar belanja.
- Pencarian cepat (judul/author) untuk cek sebelum membeli.
- Bisa diakses dari HP saat di toko.

---

## 4. Tujuan & Sasaran

### Tujuan Produk
Membantu pemilik koleksi mengetahui dengan pasti **volume apa saja yang sudah dan belum dimiliki** untuk setiap judul, dengan input yang cepat dan hasil yang mudah dibaca.

### Sasaran Terukur (MVP)
| Metrik | Target |
|---|---|
| Waktu tambah 1 judul (tanpa volume) | < 30 detik |
| Waktu mencatat 1 judul dengan 64 volume bolong lewat input rentang | < 60 detik |
| Waktu cek "volume X dari judul Y sudah punya?" | < 5 detik (cari judul, lihat petak) |
| Waktu menambah petak untuk volume baru terbit | < 10 detik |
| Waktu muat halaman utama (500 judul) | < 2 detik |
| Field wajib saat tambah judul | 1 (judul) |
| Biaya | 0 rupiah |

### Non-Tujuan (Saat Ini)
- Bukan pembaca manga / tidak menyimpan file konten manga.
- Bukan toko atau platform berbagi koleksi publik.
- Tidak terhubung ke database manga eksternal, jadi total volume diisi manual.
- Tidak mencatat harga, tanggal beli, atau kondisi fisik per volume (opsi Fase 3).

---

## 5. Target Pengguna (Persona)

**Pengguna Utama: "Kolektor Personal"**
- Satu orang, tanpa multi-user di MVP.
- Punya 20–500 judul, sebagian lengkap, sebagian **bolong-bolong**, fisik dan/atau digital.
- Memakai HP (saat di toko) dan laptop (saat merapikan data).
- Ingin cepat tahu "volume berapa yang belum saya punya?" sebelum membeli.

**Pengguna Sekunder (Opsional, Fase 4):** teman/keluarga yang melihat daftar (read-only).

---

## 6. Ruang Lingkup (Scope)

### In-Scope (MVP)
- ✅ CRUD judul manga
- ✅ **Tracking per volume**: tandai nomor volume yang dimiliki
- ✅ **Input cepat**: ketuk petak volume, atau ketik rentang (`1-20, 25, 30-44`) dengan mode Tambah / Hapus / Ganti semua
- ✅ **Total volume bisa diubah kapan saja** (petak mengikuti) dan **status rilis** Ongoing/Tamat, termasuk tombol "+ Volume baru terbit"
- ✅ **Ringkasan kekurangan** per judul ("Belum punya: ...") dengan tombol Salin
- ✅ **Daftar kurang** lintas judul (daftar belanja), bisa disalin/diunduh
- ✅ Field judul: judul, author, total volume, status rilis, status baca (opsional), rating, catatan, cover URL
- ✅ Pencarian teks (judul / author)
- ✅ Filter: kelengkapan, status baca, rating. Sort: abjad, terbaru, paling banyak kurang
- ✅ Dashboard statistik
- ✅ Tampilan kartu (grid) + daftar (tabel)
- ✅ Cover lewat **URL** dengan placeholder inisial judul
- ✅ Responsif (mobile-first untuk dipakai di toko)
- ✅ **Ekspor** data (CSV/JSON) sebagai backup
- ✅ Peringatan judul serupa saat tambah entri

### Out-of-Scope (MVP)
- ❌ Genre, lokasi penyimpanan (dihapus)
- ❌ Autentikasi multi-user / registrasi
- ❌ Sinkronisasi real-time, integrasi API manga eksternal, e-commerce
- ❌ Upload file gambar / penyimpanan file manga
- ❌ Edisi khusus bernomor non-bulat (mis. 5.5, omnibus, box set); catat di kolom catatan

### Definisi Penting

| Istilah | Definisi |
|---|---|
| Dimiliki | Jumlah nomor volume yang ditandai dimiliki |
| Nomor tertinggi dimiliki | Nomor volume terbesar yang dimiliki |
| Total volume | Tamat: jumlah volume final. Ongoing: volume terbit terakhir yang diketahui (diperbarui manual) |
| Kurang | Nomor volume dalam rentang 1..`total_volume` yang belum dimiliki. Bila total belum diketahui (0), kurang dihitung hanya sampai nomor tertinggi dimiliki |
| Bolong | Ada nomor kosong **di bawah** nomor tertinggi yang dimiliki |
| Volume kurang (dashboard) | Jumlah seluruh volume kurang dari semua judul |
| Judul belum lengkap (dashboard) | Judul dengan dimiliki > 0 dan kurang > 0. Judul ongoing yang sudah Terbaru dan judul Kosong tidak dihitung |

**Status kelengkapan** (dihitung otomatis, tidak diinput):

| Status | Kondisi |
|---|---|
| Lengkap | Status rilis **tamat**, `total_volume > 0`, dan semua nomor 1..total dimiliki |
| Terbaru | Status rilis **ongoing** dan semua nomor 1..total (terbit sejauh ini) dimiliki |
| Ada bolong | Ada nomor kosong di bawah nomor tertinggi dimiliki |
| Belum sampai akhir | Tidak ada bolong, tetapi nomor tertinggi dimiliki < `total_volume` (ongoing: ditampilkan "Belum sampai terbaru") |
| Kosong | Belum punya satu volume pun |

Bila total belum diketahui dan tidak ada bolong, status ditampilkan "Berurutan sampai vol N (total belum diketahui)".

**Contoh tamat:** Judul total 64, dimiliki 1-20, 25-30, 41-46 (32 volume) → status **Ada bolong**, "Belum punya: 21-24, 31-40, 47-64".

**Contoh ongoing:** One Piece, ongoing, total 112 (terbit sejauh ini), dimiliki 1-112 → status **Terbaru sampai vol 112**. Saat vol 113 terbit, total dinaikkan jadi 113 → status berubah menjadi **Belum sampai terbaru**, "Belum punya: 113".

---

## 7. Fitur & Prioritas (MoSCoW)

*Catatan: penomoran ID diatur ulang dari v1.1.*

### Must-Have (Wajib: MVP)
| ID | Fitur | Deskripsi |
|---|---|---|
| F-01 | Tambah Judul | Form dengan 1 field wajib (judul); total volume diisi bila diketahui |
| F-02 | Lihat Daftar | Grid kartu & tabel, pagination maks. 24 per halaman; tiap kartu menampilkan "32/64" + bar segmen per volume |
| F-03 | Edit & Hapus | Ubah data; dialog konfirmasi hapus (menghapus judul juga menghapus catatan volumenya) |
| F-04 | Detail Judul | Info judul + petak volume + ringkasan kekurangan |
| F-05 | Pencarian | Judul/author; hasil langsung menampilkan ringkasan "Belum punya" |
| F-06 | Filter & Sort | Filter kelengkapan, status baca, rating; sort abjad, terbaru, paling banyak kurang |
| F-07 | Status Baca (opsional) | Belum dibaca / Sedang dibaca / Selesai / Dihentikan; default "belum" |
| F-08 | Dashboard | Total judul, Volume dimiliki, Volume kurang, Judul belum lengkap |
| F-09 | Penyimpanan Data | SQLite persisten (Bagian 11) |
| F-10 | **Petak Volume** | Grid nomor 1..total; ketuk untuk menandai dimiliki/belum. Jumlah petak otomatis mengikuti total volume |
| F-11 | **Input Rentang** | Ketik `1-20, 25, 30-44` → pratinjau → terapkan dengan mode **Tambah** (default), **Hapus**, atau **Ganti semua**. Tombol "Punya semua" dan "Kosongkan" |
| F-12 | **Ringkasan Kekurangan** | Teks otomatis "Belum punya: 21-24, 31-40, 45-64" + tombol Salin |
| F-13 | **Daftar Kurang** | Halaman gabungan semua judul yang belum lengkap, bisa disalin dan diunduh (TXT/CSV) |
| F-14 | Cover URL + Placeholder | Field URL opsional; kosong/gagal → placeholder inisial judul |
| F-15 | Ekspor | Unduh seluruh data (termasuk volume) sebagai CSV/JSON |
| F-16 | Cek Duplikat | Peringatan bila judul serupa sudah ada (tetap boleh disimpan) |
| F-17 | **Status Rilis & Volume Baru Terbit** | Penanda Ongoing/Tamat; total volume bisa diubah dengan - / +; untuk ongoing ada tombol "+ Volume baru terbit" yang menambah satu petak kosong di ujung |

### Should-Have (Fase 2)
| ID | Fitur | Deskripsi |
|---|---|---|
| F-18 | Impor | Restore dari JSON/CSV hasil ekspor, dengan pratinjau sebelum menimpa |
| F-19 | Sudah Dibaca per Volume | Penanda baca per nomor volume |
| F-20 | Rating & Catatan Lanjutan | Rating bintang interaktif, catatan panjang |
| F-21 | Validasi Cover | Tandai cover yang gagal dimuat |
| F-22 | Edit Massal Volume | Pilih beberapa judul dan tandai rentang yang sama (mis. baru beli paket) |

### Could-Have (Fase 3)
| ID | Fitur | Deskripsi |
|---|---|---|
| F-23 | Wishlist | Judul yang ingin dibeli tetapi belum dimiliki |
| F-24 | Tag / Koleksi | Grup custom (mis. "Favorit") |
| F-25 | Peminjaman | Catat volume yang dipinjam, oleh siapa, kapan kembali |
| F-26 | Info Beli per Volume | Tanggal beli, harga, toko |
| F-27 | Edisi Khusus | Nomor non-bulat, omnibus, box set |
| F-28 | Statistik Lanjutan | Grafik pembelian per bulan |
| F-29 | Mode Terang | Varian terang (abu tua jadi default) |

### Won't-Have (Saat Ini)
Multi-user, login OAuth, integrasi toko, pembaca manga, genre, lokasi penyimpanan.

---

## 8. User Stories

- **US-01**: Sebagai kolektor, saya ingin menambah judul baru dengan cepat agar koleksi selalu terupdate.
- **US-02**: Sebagai kolektor, saya ingin mencari judul/author agar menemukan manga dalam hitungan detik.
- **US-03**: Sebagai kolektor, saya ingin menandai **volume nomor berapa saja** yang saya miliki, walau tidak berurutan, agar catatan saya akurat.
- **US-04**: Sebagai kolektor, saya ingin mengetik rentang (mis. `1-20, 25, 30-44`) agar tidak perlu menandai puluhan petak satu per satu.
- **US-05**: Sebagai kolektor, saya ingin melihat daftar volume yang **belum** saya punya per judul agar tahu apa yang perlu dicari.
- **US-06**: Sebagai kolektor, saya ingin satu **Daftar kurang** gabungan agar bisa dibawa saat belanja dan tidak membeli ganda.
- **US-07**: Sebagai kolektor, saya ingin memfilter judul yang bolong atau belum lengkap agar fokus melengkapinya.
- **US-08**: Sebagai kolektor, saya ingin backup data agar tidak hilang saat perangkat bermasalah.
- **US-09**: Sebagai kolektor, saya ingin antarmuka yang enak di HP agar bisa cek koleksi saat di toko.
- **US-10**: Sebagai kolektor, saya ingin diperingatkan bila judul yang saya tambah sudah ada.
- **US-11**: Sebagai kolektor, saya ingin menambah petak saat ada volume baru terbit di judul yang masih ongoing, agar volume baru itu langsung tercatat sebagai kekurangan.
- **US-12**: Sebagai kolektor, saya ingin mengubah total volume kapan saja (naik atau turun) tanpa kehilangan catatan volume yang sudah ada.

---

## 9. Alur Pengguna (User Flow)

```
[Buka Dashboard]
      |
      +--> [Statistik + Daftar Judul]
      |          |
      |          +--> [Cari / Filter kelengkapan] --> [Detail Judul]
      |                                                   |
      |                                                   +--> [Petak Volume: ketuk / ketik rentang]
      |                                                   +--> [Ringkasan "Belum punya" -> Salin]
      |                                                   +--> [Edit / Hapus]
      |
      +--> [+ Tambah Judul] --> [Isi Form] --> [Cek duplikat] --> [Simpan] --> [Detail Judul: isi volume]
      |
      +--> [Daftar kurang] --> [Salin / Unduh]  (dibawa saat belanja)
      |
      +--> [Pengaturan] --> [Ekspor Data]  (Impor: Fase 2)
```

**Alur utama: mencatat judul yang bolong**
1. Tambah judul, isi total volume (mis. 64).
2. Di detail, ketik `1-20, 25-30, 41-46` pada input rentang.
3. Lihat pratinjau ("32 volume dimiliki, 32 kurang"), tekan Terapkan.
4. Rapikan dengan mengetuk petak yang salah.
5. Ringkasan "Belum punya: 21-24, 31-40, 47-64" muncul otomatis.

**Alur: volume baru terbit (judul ongoing)**
1. Buka detail judul, tekan **+ Volume baru terbit**. Total naik 1 dan satu petak kosong muncul.
2. Bila volume itu sudah dibeli, ketuk petaknya; bila belum, biarkan. Ia otomatis masuk Daftar kurang.
3. Bila judul tamat, ubah status ke **Tamat**. Total dipertahankan sebagai total final.

---

## 10. Model Data (Schema)

### Entitas: `manga`

| Field | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `id` | INTEGER (autoincrement) | Ya | Primary key |
| `judul` | TEXT | Ya | Nama manga, maks. 200 karakter |
| `judul_norm` | TEXT | Ya (otomatis) | Judul ternormalisasi untuk cek duplikat/pencarian |
| `author` | TEXT | Tidak | Nama pengarang |
| `status_rilis` | ENUM | Tidak | `ongoing` (default) atau `tamat` |
| `total_volume` | INTEGER | Tidak | Tamat: total final. Ongoing: volume terbit sejauh ini. 0 = belum diketahui. Maks. 1000 |
| `status_baca` | ENUM | Tidak | `belum` (default), `sedang`, `selesai`, `dihentikan` |
| `rating` | INTEGER | Tidak | 1–5 |
| `catatan` | TEXT | Tidak | Catatan bebas (mis. edisi khusus yang tidak masuk nomor) |
| `cover_url` | TEXT | Tidak | Link http/https; kosong = placeholder |
| `tanggal_tambah` | DATETIME | Ya | Otomatis |
| `tanggal_update` | DATETIME | Ya | Otomatis; ikut diperbarui saat volume berubah |

### Entitas: `volume`

| Field | Tipe | Keterangan |
|---|---|---|
| `manga_id` | INTEGER | FK ke `manga.id`, `ON DELETE CASCADE` |
| `nomor` | INTEGER | Nomor volume, 1–1000 |

- Primary key gabungan (`manga_id`, `nomor`).
- **Hanya volume yang dimiliki yang disimpan** (ada baris = dimiliki). Volume yang kurang dihitung, bukan disimpan. Cara ini otomatis mendukung judul yang total volumenya belum diketahui.
- `dimiliki` = jumlah baris; `kurang`, `bolong`, dan status kelengkapan dihitung dari baris ini + `total_volume`.

### Aturan Validasi
- `judul` wajib; `status_baca` salah satu enum; `rating` kosong atau 1–5; `cover_url` kosong atau diawali `http://`/`https://`.
- `total_volume` bilangan bulat 0–1000.
- Bila `total_volume` diturunkan di bawah nomor tertinggi yang dimiliki: **tolak** dengan pesan "Volume N masih dimiliki. Hapus dulu sebelum menurunkan total." Tidak ada volume yang dihapus otomatis.
- Bila nomor yang dimasukkan > `total_volume`: **tolak** dengan pesan "Volume N melebihi total M. Naikkan total dulu."
- Tombol "+ Volume baru terbit" (hanya untuk ongoing) menaikkan `total_volume` sebesar 1 dan **tidak** menandai volume baru sebagai dimiliki.
- Mengubah status rilis dari Ongoing ke Tamat mempertahankan total apa adanya; tombol "+ Volume baru terbit" disembunyikan untuk Tamat.

### Aturan Parser Rentang (F-11)
- Pemisah: koma atau spasi. Format: angka `25` atau rentang `30-44`.
- Rentang terbalik (`44-30`), nomor 0, nomor > 1000, atau karakter lain → tampilkan pesan error spesifik dan **jangan terapkan apa pun**.
- Nomor yang tumpang tindih digabung (`1-10, 5-15` → 1–15).
- Tiga mode: **Tambah** (menambah ke yang sudah ada; **default**), **Hapus** (mencabut nomor yang diketik dari yang dimiliki), dan **Ganti semua** (isi input menjadi satu-satunya kebenaran; dipilih sengaja, pratinjau menampilkan jumlah yang akan hilang, mis. "+8 volume, −2 volume").
- Fungsi `kompres_rentang([21,22,23,24,31,...]) → "21-24, 31-40"` dipakai untuk ringkasan dan ekspor; keduanya wajib punya unit test.

---

## 11. Database

### ✅ Keputusan: **SQLite** untuk MVP

| Aspek | Penilaian |
|---|---|
| Biaya | Gratis |
| Setup | Tanpa server |
| Bentuk | Satu file (`manga.db`), backup = salin file |
| Cocok untuk | Single-user, web lokal |
| Performa | Cukup. Contoh: 500 judul × rata-rata 40 volume = sekitar 20.000 baris `volume`, sangat ringan dengan indeks pada `manga_id` |

- Aktifkan `PRAGMA foreign_keys = ON` agar `ON DELETE CASCADE` bekerja di SQLite.
- Akses data lewat ORM (SQLModel/SQLAlchemy) agar migrasi ke Postgres/Supabase mudah.
- Operasi "terapkan rentang" dijalankan dalam **satu transaksi**.

### Alternatif untuk Fase 4
Supabase (Postgres), Firebase Firestore, MongoDB Atlas, PostgreSQL self-host. Untuk skema relasional ini, Supabase/Postgres paling natural. Periksa ulang batas free tier di situs resminya sebelum memutuskan.

---

## 12. Stack Teknologi (Ditetapkan)

Pendekatan: **server-rendered + HTMX**, tanpa SPA dan tanpa build step frontend.

| Layer | Pilihan | Alasan |
|---|---|---|
| Backend | **FastAPI** (alternatif: Flask) | Ringan, validasi bawaan |
| Template | **Jinja2** | HTML biasa, mudah diubah |
| Interaksi | **HTMX + Alpine.js** | Ketuk petak volume, pratinjau rentang, filter, dialog hapus tanpa SPA |
| Styling | **CSS biasa + CSS variables** | Token dari `DESIGN.md`, tanpa compiler |
| Database | **SQLite + SQLModel/SQLAlchemy** | Bagian 11 |
| Font | Press Start 2P + IBM Plex Sans, di-host lokal | Gratis, tanpa CDN |
| Hosting | Lokal → Render/Fly free tier (Fase 4) | 0 rupiah |

**Interaksi petak volume:** ketuk petak mengirim satu request kecil (HTMX) yang mengganti status satu nomor dan memperbarui petak, bar progres, dan ringkasan "Belum punya" dalam satu respons.

**Struktur proyek yang disarankan**
```
mangashelf/
├── app/
│   ├── main.py
│   ├── models.py          # Manga, Volume
│   ├── db.py
│   ├── rentang.py         # parse_rentang(), kompres_rentang(), hitung_kelengkapan()
│   ├── routes/            # manga.py, volume.py, daftar_kurang.py, export.py
│   ├── templates/         # base, index, detail, form, daftar_kurang, partial: _card, _row, _petak_volume
│   └── static/            # css/tokens.css, base.css, components.css · js/htmx, alpine · fonts/
├── tests/test_rentang.py
├── data/manga.db          # .gitignore
├── seed.py
├── requirements.txt
└── README.md
```

---

## 13. Tampilan & UX

Panduan visual lengkap: **`DESIGN.md`**. Arah: **minimalis, retro Nintendo, abu tua**; satu aksen merah hanya untuk aksi utama.

**Dashboard**
- Header: nama aplikasi + pencarian + tombol "Tambah judul".
- Kartu statistik: Total judul · Volume dimiliki · Volume kurang · Judul belum lengkap. Kartu "Volume kurang" menuju Daftar kurang.
- Toolbar: filter kelengkapan (Semua / Ada bolong / Belum sampai akhir / Lengkap / Kosong) + status baca + sort + toggle grid/daftar.
- Kartu judul: cover (atau placeholder), judul, author, badge kelengkapan, "32/64", bar segmen per volume.

**Halaman Detail (halaman paling penting)**
- Info judul (cover, judul, author, status baca, rating, catatan).
- **Status rilis** (Ongoing / Tamat) sebagai toggle, dan **total volume** dengan tombol - / + di atas grid.
- Tombol **+ Volume baru terbit** (hanya Ongoing).
- **Petak volume** 1..total: terisi = dimiliki, putus-putus = belum.
- Input rentang dengan tombol **Tambah** dan **Hapus** (Ganti semua ada di menu lanjutan), pratinjau, serta "Punya semua" / "Kosongkan".
- Ringkasan "Belum punya: ..." dengan tombol Salin.
- Tombol Edit / Hapus / Kembali.

**Halaman Daftar kurang**
- Per judul: nama + "Belum punya: ..." + jumlah kurang. Urut default: paling sedikit kurang dulu (paling dekat lengkap), bisa diganti.
- Judul ongoing menampilkan kekurangan hanya sampai volume terbit terakhir yang tercatat; judul Terbaru tidak muncul. Judul dengan total belum diketahui diberi tanda "sampai vol N saja".
- Tombol Salin semua dan Unduh (TXT/CSV).

**Form Tambah/Edit**
- Wajib: Judul. Opsional: author, status rilis (default Ongoing), total volume, status baca, rating, catatan, cover URL.
- Peringatan judul serupa sebelum menyimpan.

**Pengaturan:** Ekspor CSV/JSON (Impor: Fase 2).

**Prinsip UX:** minimal klik, konfirmasi sebelum hapus, umpan balik jelas ("Tersimpan", "Rentang tidak valid: 44-30 terbalik").

---

## 14. Requirements Non-Fungsional

| Kategori | Kebutuhan |
|---|---|
| Performa | Halaman utama < 2 detik untuk 500 judul; ketuk petak volume terasa instan (< 300 ms) |
| Performa Cover | Lazy loading + pagination maks. 24 kartu; placeholder tampil lebih dulu |
| Skala volume | Mendukung judul hingga 1000 volume (petak ditata dengan grid, tanpa membuat halaman berat) |
| Kemudahan | Bisa dipakai tanpa pelatihan |
| Responsif | Baik di HP ≥ 360px (petak 44px, mudah diketuk) & desktop |
| Aksesibilitas | Kontras ≥ 4.5:1, fokus keyboard terlihat, status petak tidak hanya lewat warna, hormati `prefers-reduced-motion` |
| Keandalan | Data persisten; ekspor mencakup volume; operasi rentang atomik (transaksi) |
| Keamanan | Validasi di server, query terparameter via ORM, auto-escape Jinja2 (cegah XSS), CSRF token pada form dan aksi ketuk |
| Keamanan (bila online) | Tanpa login, siapa pun yang tahu URL bisa mengubah data. Sebelum hosting publik wajib ada gerbang kata sandi atau mode read-only |
| Kompatibilitas | Chrome, Firefox, Safari, Edge terbaru |
| Biaya | 0 rupiah |

---

## 15. Roadmap Pengembangan

| Fase | Fitur | Estimasi |
|---|---|---|
| **Fase 1: MVP** | F-01 s/d F-17 (CRUD, petak volume, input rentang, ringkasan kekurangan, Daftar kurang, pencarian, filter kelengkapan, dashboard, cover URL, ekspor, cek duplikat) | 2 minggu |
| **Fase 2** | Impor, sudah dibaca per volume, rating/catatan lanjutan, validasi cover, edit massal | 1–2 minggu |
| **Fase 3** | Wishlist, tag, peminjaman, info beli, edisi khusus, statistik, mode terang | 2–3 minggu |
| **Fase 4 (opsional)** | Hosting online + Supabase, gerbang kata sandi, read-only share | Fleksibel |

**Urutan kerja MVP yang disarankan**
1. Kerangka proyek, model `Manga` + `Volume`, SQLite (foreign key aktif), `seed.py`.
2. **`rentang.py` + unit test** (parser, kompres, kelengkapan). Ini logika inti; selesaikan dulu.
3. Token CSS dari `DESIGN.md` + layout dasar.
4. Form tambah/edit + validasi + cek duplikat.
5. Halaman detail: petak volume, input rentang + pratinjau, ringkasan kekurangan.
6. Daftar (grid/tabel), bar segmen, badge kelengkapan, pagination.
7. Pencarian, filter kelengkapan, sort lewat HTMX.
8. Dashboard, Daftar kurang, ekspor.
9. Uji di lebar 360px, 640px, 1120px dan dengan data 64 dan 1000 volume.

---

## 16. Metrik Keberhasilan

- Jumlah judul dan volume tercatat bertambah dari waktu ke waktu (adopsi).
- Judul dengan 64 volume bolong bisa dicatat < 60 detik lewat input rentang.
- Tidak ada pembelian ganda (dicek lewat pencarian atau Daftar kurang saat di toko).
- Volume baru terbit bisa ditambahkan ke catatan dalam < 10 detik.
- Angka "Volume dimiliki" dan "Volume kurang" di dashboard selalu cocok dengan petak volume (tidak ada selisih).
- Data bisa diekspor, dan dipulihkan 100% setelah impor tersedia.

---

## 17. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| Input volume satu per satu terlalu lama | Input rentang + "Punya semua" + pratinjau selisih; target < 60 detik per judul |
| Salah ketik rentang menimpa data bagus | Pratinjau selisih sebelum menerapkan, validasi ketat, tidak ada perubahan bila ada error |
| Total volume berubah (judul ongoing) | Total bisa diubah kapan saja lewat - / + dan "+ Volume baru terbit"; menurunkan total di bawah volume yang dimiliki ditolak; status "Terbaru" mencegah judul ongoing selalu tampak kurang |
| Lupa memperbarui total saat volume baru terbit | Total ongoing diisi manual (tidak ada sumber eksternal); risiko diterima di MVP, integrasi data eksternal jadi opsi Fase 4 |
| Angka tidak sinkron dengan daftar volume | Jumlah dimiliki **dihitung** dari tabel `volume`, bukan disimpan terpisah |
| Data hilang | Ekspor rutin + simpan `manga.db` di cloud/flashdisk |
| Duplikat entri | Pencarian cepat + peringatan judul serupa |
| Edisi khusus tidak muat di nomor bulat | Catat di `catatan` pada MVP; fitur khusus di Fase 3 |
| Cover link rusak | Validasi URL + fallback placeholder |
| Data terbuka bila di-host tanpa login | Gerbang kata sandi sebelum hosting publik |
| Migrasi DB ke online | ORM + skema relasional |

---

## 18. Asumsi & Ketergantungan

- **Single user**; tidak ada login di MVP (dijalankan lokal).
- Koleksi bersifat privat dan hanya metadata, bukan konten manga.
- Penomoran volume berupa bilangan bulat 1–1000; edisi khusus dicatat manual di catatan.
- Total volume diisi pengguna dan, untuk judul ongoing, diperbarui manual saat volume baru terbit (tidak ada sumber data eksternal).
- Internet hanya dibutuhkan untuk memuat gambar cover dari URL.
- Gaya visual terinspirasi konsol retro; tidak memakai logo, karakter, atau aset merek mana pun.

---

## 19. Lampiran — Contoh Data Awal (Seed)

`volume_dimiliki` di seed ditulis sebagai teks rentang agar mudah dibaca; `seed.py` mengubahnya menjadi baris tabel `volume` memakai parser rentang yang sama.

```json
[
  {
    "judul": "One Piece",
    "author": "Eiichiro Oda",
    "status_rilis": "ongoing",
    "total_volume": 112,
    "status_baca": "sedang",
    "volume_dimiliki": "1-105",
    "rating": 5,
    "catatan": "Kurang vol 106-112.",
    "cover_url": ""
  },
  {
    "judul": "Attack on Titan",
    "author": "Hajime Isayama",
    "status_rilis": "tamat",
    "total_volume": 34,
    "status_baca": "selesai",
    "volume_dimiliki": "1-34",
    "rating": 5,
    "catatan": "Lengkap.",
    "cover_url": ""
  },
  {
    "judul": "Naruto",
    "author": "Masashi Kishimoto",
    "status_rilis": "tamat",
    "total_volume": 72,
    "status_baca": "belum",
    "volume_dimiliki": "1-24, 30-42, 55-72",
    "rating": 4,
    "catatan": "Contoh koleksi bolong: kurang 25-29 dan 43-54.",
    "cover_url": ""
  }
]
```

Hasil yang diharapkan untuk contoh pertama: ongoing, dimiliki 105 dari 112, status **Belum sampai terbaru**, "Belum punya: 106-112".

Hasil yang diharapkan untuk contoh ketiga: dimiliki 55, kurang 17, status **Ada bolong**, ringkasan "Belum punya: 25-29, 43-54".

---

### Catatan Penutup
Hal yang masih perlu dikonfirmasi sebelum membangun:
1. Nama aplikasi (MangaShelf → ganti?)
2. Apakah `status_baca` masih dipakai, atau dihapus sekalian agar lebih ringkas?
3. Apakah ada judul dengan edisi khusus (nomor desimal, omnibus, box set) yang ingin dicatat sejak MVP? Jika ya, F-27 dinaikkan prioritasnya.
4. Backend FastAPI (disarankan) atau Flask/Node?
5. Apakah akan di-host online (Fase 4)? Jika ya, gerbang kata sandi dikerjakan lebih awal.
