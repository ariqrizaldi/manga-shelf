# DESIGN.md — MangaShelf

> Panduan desain visual. Arah: **minimalis, retro Nintendo, abu tua.**
> Acuan rasa: bodi konsol era Famicom / Super Famicom, bukan game arcade yang ramai. Tenang, padat, fungsional.

---

## 1. Prinsip

1. **Abu tua jadi panggung.** Hampir seluruh layar abu tua. Warna cerah hanya muncul untuk hal yang bermakna (aksi utama, status).
2. **Satu momen yang diingat: tombol merah.** Seperti tombol A di controller. Hanya aksi utama ("Tambah manga", "Simpan") yang berwarna merah. Selain itu netral.
3. **Bentuk keras, bukan lembut.** Sudut tajam, border tebal, bayangan solid tanpa blur. Tidak ada gradasi, tidak ada glow.
4. **Piksel hanya di judul.** Font piksel dipakai hemat untuk judul halaman dan angka statistik. Teks bacaan memakai font yang nyaman.
5. **Gerak hanya sebagai jawaban atas aksi.** Tombol "tertekan", kartu terbuka. Tidak ada animasi masuk otomatis.
6. **Fungsi di atas gaya.** Retro tidak boleh mengorbankan keterbacaan atau kecepatan (target: tambah entri < 30 detik).

---

## 2. Warna

Palet inti (6 warna) + 4 warna status dari tombol SNES.

| Token | Hex | Pakai untuk |
|---|---|---|
| `--bg` | `#2a2b2f` | Latar halaman |
| `--surface` | `#36383d` | Kartu, panel, form |
| `--surface-raised` | `#43454b` | Hover, input aktif, baris tabel selang-seling |
| `--ink` | `#ebe7dc` | Teks utama (krem hangat, bukan putih murni) |
| `--ink-muted` | `#a6a49c` | Teks sekunder, label |
| `--line` | `#17181b` | Border & bayangan solid (hampir hitam) |
| `--accent` | `#d6202b` | Aksi utama, fokus penting (merah Famicom) |

**Warna status baca** (terinspirasi tombol Super Famicom):

| Status | Token | Hex | Catatan |
|---|---|---|---|
| Belum dibaca | `--st-belum` | `#8a8c93` | Abu, sengaja netral |
| Sedang dibaca | `--st-sedang` | `#e0b32a` | Kuning (tombol Y) |
| Selesai | `--st-selesai` | `#3f9b5a` | Hijau |
| Dihentikan | `--st-henti` | `#4a6fc4` | Biru |

Aturan:
- Teks di atas `--accent` memakai `--ink`; teks di atas kuning memakai `--line`.
- Jangan pakai merah untuk status. Merah hanya untuk aksi utama dan hapus (lihat Komponen).
- Cek kontras ≥ 4.5:1 untuk teks bacaan sebelum dirilis.

---

## 3. Tipografi

| Peran | Font | Fallback | Dipakai untuk |
|---|---|---|---|
| Tampilan | **Press Start 2P** | `monospace` | Nama aplikasi, judul halaman, angka di kartu statistik |
| Bacaan | **IBM Plex Sans** | `system-ui, sans-serif` | Semua teks lain: label, isi form, tabel, catatan |

Skala (base 16px):

| Token | Ukuran | Dipakai |
|---|---|---|
| `--fs-display` | 20px | Judul halaman (Press Start 2P) |
| `--fs-stat` | 24px | Angka statistik (Press Start 2P) |
| `--fs-lg` | 18px | Judul kartu / detail |
| `--fs-base` | 16px | Teks standar |
| `--fs-sm` | 14px | Label, meta, badge |

Aturan:
- Press Start 2P itu lebar dan tebal; **jangan** dipakai untuk paragraf, tabel, atau label kecil.
- Gunakan sentence case ("Tambah manga", bukan "TAMBAH MANGA"). Hindari huruf kapital semua.
- Line-height teks bacaan 1.5; panjang baris maks. 70 karakter.
- Untuk menekan ukuran halaman dan tetap gratis, host font sendiri (`/static/fonts`) dengan `font-display: swap`.

---

## 4. Bentuk, Jarak, dan Kedalaman

```css
:root {
  --bg: #2a2b2f;
  --surface: #36383d;
  --surface-raised: #43454b;
  --ink: #ebe7dc;
  --ink-muted: #a6a49c;
  --line: #17181b;
  --accent: #d6202b;

  --st-belum: #8a8c93;
  --st-sedang: #e0b32a;
  --st-selesai: #3f9b5a;
  --st-henti: #4a6fc4;

  --font-display: "Press Start 2P", monospace;
  --font-body: "IBM Plex Sans", system-ui, sans-serif;

  --radius: 2px;
  --border: 2px solid var(--line);
  --shadow: 4px 4px 0 var(--line);      /* solid, tanpa blur */
  --shadow-pressed: 1px 1px 0 var(--line);

  --space-1: 4px;  --space-2: 8px;  --space-3: 12px;
  --space-4: 16px; --space-5: 24px; --space-6: 32px;
}
```

- **Radius:** 2px di semua elemen. Tidak ada pil/bulat, kecuali tidak diperlukan sama sekali.
- **Border:** selalu 2px `--line`.
- **Bayangan:** hanya bayangan solid offset 4px. Tidak ada `blur`, tidak ada `rgba` lembut.
- **Jarak:** kelipatan 4px. Padding kartu 16px, jarak antar kartu 16px.
- **Alignment:** rata kiri untuk semua konten. Hanya angka statistik yang boleh rata tengah di dalam kartunya.

---

## 5. Komponen

### Tombol
| Varian | Gaya | Dipakai |
|---|---|---|
| Utama | latar `--accent`, teks `--ink`, border + bayangan | "Tambah manga", "Simpan" |
| Biasa | latar `--surface-raised`, teks `--ink`, border + bayangan | "Batal", "Ekspor", "Edit" |
| Hapus | latar `--surface`, teks & border `--accent` | "Hapus" (merah hanya sebagai garis) |

Interaksi: saat ditekan, tombol bergeser `translate(3px, 3px)` dan bayangan jadi `--shadow-pressed`. Efek "tombol fisik ditekan", tanpa transisi lama (≤ 80ms).

### Input & form
- Latar `--bg`, border 2px `--line`, teks `--ink`.
- Fokus: outline 2px `--accent` dengan offset 2px (wajib terlihat untuk keyboard).
- Label di atas input, `--fs-sm`, warna `--ink-muted`.
- Field wajib (Judul, Status baca) diberi tanda `*` dan pesan error di bawah field.

### Kartu manga (grid)
```
┌──────────────┐
│  [ cover ]   │  rasio 2:3
│              │
├──────────────┤
│ Judul        │  --fs-lg, maks. 2 baris
│ Author       │  --fs-sm, muted
│ [Selesai]    │  badge status
│ vol 34/34    │  bar progres
└──────────────┘
```
- Latar `--surface`, border 2px, bayangan solid.
- Hover: kartu naik `translate(-2px, -2px)` dan bayangan jadi 6px. Tidak ada transisi warna.
- **Placeholder cover:** blok persegi panjang rasio 2:3 berlatar `--surface-raised`, berisi inisial judul (1–2 huruf, Press Start 2P, `--ink-muted`). Diganti gambar setelah termuat (`loading="lazy"`).

### Badge status
- Kotak kecil, border 2px `--line`, latar sesuai token status, teks `--line` (atau `--ink` pada hijau/biru).
- Isi teks status lengkap ("Sedang dibaca"), jangan hanya warna, agar tetap terbaca bagi buta warna.

### Toggle segmen dan stepper
- **Toggle Ongoing / Tamat:** dua tombol berdampingan, border 2px, tanpa bayangan. Yang aktif berlatar `--ink` dengan teks `--line`; yang tidak aktif berlatar `--surface` dengan teks `--ink-muted`.
- **Stepper total:** tombol `-` dan `+` (44px) mengapit angka di tengah (Press Start 2P, `--fs-lg`).

### Badge kelengkapan
Dipakai di kartu dan halaman detail. Teks selalu ditampilkan.

| Status | Warna | Teks pada badge |
|---|---|---|
| Lengkap / Terbaru | `--st-selesai` | `--ink` |
| Ada bolong | `--st-sedang` | `--line` |
| Belum sampai akhir / terbaru | `--st-henti` | `--ink` |
| Kosong | `--st-belum` | `--line` |

### Bar progres volume
- Tinggi 8px, latar `--bg`, border 2px, isi bersegmen (blok-blok kecil) memakai `repeating-linear-gradient` tegas, bukan gradasi halus.
- Bar dibagi **satu segmen per volume** (maks. 64 segmen; di atas itu digabung per kelompok). Segmen terisi `--ink` = dimiliki, kosong = belum dimiliki, sehingga bolong langsung terlihat.
- Teks "32/64" di samping, `--fs-sm`.

### Petak volume (inti aplikasi)
Grid nomor volume di halaman detail, satu petak per nomor (1..total).

| Kondisi | Gaya |
|---|---|
| Dimiliki | Latar `--ink`, angka `--line`, border 2px solid |
| Belum dimiliki | Latar `--bg`, angka `--ink-muted`, border 2px **putus-putus** |

- Ukuran petak 44×44px (target sentuh), jarak 6px, angka `--fs-sm`.
- Ketuk petak untuk mengganti status; efek "tertekan" seperti tombol (translate 2px).
- Beda dimiliki/belum tidak hanya soal warna: terisi vs putus-putus, jadi tetap jelas bagi buta warna.
- Di bawah grid: kolom **input rentang** (mis. `1-20, 25, 30-44`) dengan dua tombol, **Tambah** dan **Hapus**. "Ganti semua" ada di menu lanjutan agar tidak terpencet tanpa sengaja. Di sampingnya ada "Punya semua" dan "Kosongkan".
- Di atas grid: toggle **Ongoing / Tamat**, label total ("Volume terbit sejauh ini" untuk Ongoing, "Total volume (final)" untuk Tamat), dan stepper **- / +** untuk mengubah total. Grid langsung menambah atau mengurangi petak.
- Tombol **+ Volume baru terbit (vol N+1)** hanya tampil untuk Ongoing, lebar penuh, berwarna `--accent`. Ini satu-satunya tombol utama di halaman detail untuk judul Ongoing.
- Pesan error tampil tepat di bawah input, warna merah muda terang (`#ff8a8a`), tanpa dialog. Contoh: "Volume 30 melebihi total 24. Naikkan total dulu."
- Di bawah grid: teks "Belum punya: 21-24, 31-40, 45-64" dengan tombol "Salin". Teks ini dibuat otomatis dan diringkas jadi rentang.
- Bila total volume 0 (belum diketahui), grid menampilkan sampai nomor tertinggi yang dimiliki. Bila belum ada volume sama sekali, tampil petunjuk "Isi total volume untuk membuat petak".
- Menurunkan total di bawah volume yang dimiliki ditolak dengan pesan di bawah stepper; petak tidak berubah.

### Kartu statistik
- Empat kartu: Total judul, Volume dimiliki, Volume kurang, Judul belum lengkap.
- Kartu "Volume kurang" membuka halaman Daftar kurang (daftar belanja).
- Angka Press Start 2P `--fs-stat`, label di bawahnya `--fs-sm` `--ink-muted`.
- Tanpa ikon, tanpa gradien.

### Tabel (tampilan daftar)
- Header: latar `--surface-raised`, teks `--ink`, border bawah 2px.
- Baris selang-seling `--surface` / `--bg`. Hover baris `--surface-raised`.
- Di layar < 640px, baris berubah jadi kartu bertumpuk.

### Navigasi & header
- Bar atas `--surface`, border bawah 2px. Kiri: nama "MangaShelf" (Press Start 2P, kecil). Tengah: kolom pencarian. Kanan: tombol utama "Tambah manga".
- Di HP: pencarian turun ke baris kedua; tombol utama jadi tombol tetap di pojok kanan bawah.

### Dialog hapus
- Panel `--surface` dengan border + bayangan, latar belakang gelap 60%.
- Judul: "Hapus [judul]?" Isi: "Data ini tidak bisa dikembalikan." Tombol: "Batal" (biasa) dan "Hapus" (varian hapus).

---

## 6. Tata Letak

**Dashboard**
```
┌────────────────────────────────────────────┐
│ MangaShelf     [ cari judul / author ] [+ Tambah manga] │
├────────────────────────────────────────────┤
│ [Judul] [Dimiliki] [Kurang] [Belum lengkap]│
├────────────────────────────────────────────┤
│ Filter: kelengkapan ▾ status ▾ urut ▾ [▦][☰]│
├────────────────────────────────────────────┤
│ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐              │
│ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘              │
│              « 1 2 3 »  (maks. 24/hal.)   │
└────────────────────────────────────────────┘
```

- Lebar konten maks. 1120px, di tengah halaman, padding sisi 16px (HP) / 24px (desktop).
- Grid kartu: 2 kolom (≥ 360px), 3 (≥ 640px), 4 (≥ 900px), 6 (≥ 1120px).
- Halaman detail: dua kolom di desktop (cover + info kiri, petak volume kanan), satu kolom di HP dengan petak volume tepat di bawah judul.
- Halaman Daftar kurang: satu kolom, per judul berisi nama + rentang yang belum dimiliki + tombol Salin.

---

## 7. Gerak

| Kejadian | Efek | Durasi |
|---|---|---|
| Tombol ditekan | Geser 3px + bayangan mengecil | 80ms, `steps(2)` |
| Hover kartu | Naik 2px | 80ms |
| Dialog dibuka | Muncul langsung, tanpa fade | 0ms |
| Toast sukses/gagal | Muncul dari bawah, hilang setelah 3 detik | 120ms `steps(3)` |

- Tidak ada animasi saat halaman dimuat.
- Hormati `prefers-reduced-motion`: matikan semua gerak di atas.

---

## 8. Teks Antarmuka (microcopy)

- Bahasa Indonesia, sentence case, kata kerja aktif: "Simpan", "Tambah manga", "Hapus".
- Nama aksi konsisten di seluruh alur: tombol "Simpan" menghasilkan toast "Tersimpan".
- Kondisi kosong memberi arahan: "Belum ada manga. Tambah judul pertama." + tombol utama.
- Pesan error menyebut masalah dan cara memperbaikinya: "Judul wajib diisi."
- Tanpa permintaan maaf, tanpa lelucon game ("Press start!"). Retro cukup lewat visual.

---

## 9. Aksesibilitas

- Kontras teks ≥ 4.5:1 pada semua pasangan token.
- Fokus keyboard selalu terlihat (outline `--accent`).
- Target sentuh ≥ 44×44px di HP.
- Status tidak hanya dibedakan lewat warna (selalu ada teks).
- Gambar cover punya `alt` berisi judul manga.

---

## 10. Hal yang Dihindari

- Gradasi, glow neon, bayangan blur.
- Efek scanline / CRT / noise yang menurunkan keterbacaan.
- Font piksel untuk paragraf.
- Lebih dari satu warna aksen utama di satu layar.
- Ikon bergaya piksel di mana-mana. Pakai hanya bila ikon benar-benar memperjelas (mis. toggle grid/daftar).
- Referensi langsung ke karakter/logo/merek Nintendo. Ambil rasa dan warna, bukan aset.

---

## 11. Checklist Implementasi

- [ ] Token CSS (bagian 4) dimuat sekali di `:root`
- [ ] Font di-host lokal dengan `font-display: swap`
- [ ] Semua komponen memakai token, tidak ada hex di komponen
- [ ] Placeholder cover bekerja saat URL kosong atau rusak
- [ ] Diuji di lebar 360px, 640px, 1120px
- [ ] `prefers-reduced-motion` diuji
