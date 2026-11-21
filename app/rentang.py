"""Logika inti: parser rentang, kompresi rentang, dan kelengkapan koleksi."""

from __future__ import annotations

import re

MAKS_VOLUME = 1000


class RentangError(ValueError):
    """Kesalahan input rentang yang aman ditampilkan ke pengguna."""


def _cek_nomor(n: int) -> None:
    if n < 1:
        raise RentangError(f"Nomor {n} tidak valid. Volume dimulai dari 1.")
    if n > MAKS_VOLUME:
        raise RentangError(f"Nomor {n} melebihi batas {MAKS_VOLUME}.")


def parse_rentang(teks: str) -> set[int]:
    """Ubah "1-20, 25, 30-44" menjadi himpunan nomor volume.

    Pemisah boleh koma atau spasi. Spasi di sekitar tanda hubung diabaikan.
    Bila ada satu bagian tidak valid, seluruh input dianggap gagal.
    """
    teks = (teks or "").strip()
    if not teks:
        return set()

    normal = re.sub(r"\s*-\s*", "-", teks)
    bagian = [b for b in re.split(r"[,\s]+", normal) if b]
    hasil: set[int] = set()

    for b in bagian:
        if re.fullmatch(r"\d+", b):
            n = int(b)
            _cek_nomor(n)
            hasil.add(n)
        elif re.fullmatch(r"\d+-\d+", b):
            awal, akhir = (int(x) for x in b.split("-"))
            _cek_nomor(awal)
            _cek_nomor(akhir)
            if awal > akhir:
                raise RentangError(f"Rentang {awal}-{akhir} terbalik.")
            hasil.update(range(awal, akhir + 1))
        else:
            raise RentangError(
                f"Format “{b}” tidak dikenal. Contoh: 1-20, 25, 30-44."
            )

    return hasil


def kompres_rentang(nomor) -> str:
    """Ubah himpunan nomor menjadi teks ringkas, mis. "21-24, 31-40"."""
    angka = sorted(set(nomor))
    if not angka:
        return ""

    potongan: list[str] = []
    mulai = sebelumnya = angka[0]

    for n in angka[1:]:
        if n == sebelumnya + 1:
            sebelumnya = n
            continue
        potongan.append(str(mulai) if mulai == sebelumnya else f"{mulai}-{sebelumnya}")
        mulai = sebelumnya = n

    potongan.append(str(mulai) if mulai == sebelumnya else f"{mulai}-{sebelumnya}")
    return ", ".join(potongan)


def hitung_kelengkapan(
    total_volume: int, nomor_dimiliki, status_rilis: str = "ongoing"
) -> dict:
    """Hitung angka dan status kelengkapan dari daftar volume yang dimiliki."""
    dimiliki_set = set(nomor_dimiliki)
    dimiliki = len(dimiliki_set)
    tertinggi = max(dimiliki_set) if dimiliki_set else 0
    batas = max(total_volume, tertinggi)
    kurang_nomor = [n for n in range(1, batas + 1) if n not in dimiliki_set]
    kurang = len(kurang_nomor)
    bolong = any(n not in dimiliki_set for n in range(1, tertinggi + 1))

    if dimiliki == 0:
        kunci, label = "kosong", "Kosong"
    elif total_volume > 0 and kurang == 0:
        if status_rilis == "tamat":
            kunci, label = "lengkap", "Lengkap"
        else:
            kunci, label = "terbaru", "Terbaru"
    elif bolong:
        kunci, label = "bolong", "Ada bolong"
    elif total_volume == 0:
        kunci, label = "berurutan", f"Berurutan sampai vol {tertinggi}"
    else:
        kunci = "belum"
        label = "Belum sampai terbaru" if status_rilis == "ongoing" else "Belum sampai akhir"

    if kurang_nomor:
        ringkasan = "Belum punya: " + kompres_rentang(kurang_nomor)
    elif total_volume == 0 and tertinggi > 0:
        ringkasan = f"Tidak ada kekurangan sampai vol {tertinggi} (total belum diketahui)."
    elif total_volume > 0:
        ringkasan = f"Semua volume 1–{total_volume} dimiliki."
    else:
        ringkasan = "Belum ada volume yang dimiliki."

    return {
        "dimiliki": dimiliki,
        "kurang": kurang,
        "kurang_nomor": kurang_nomor,
        "kurang_terkompres": kompres_rentang(kurang_nomor),
        "tertinggi": tertinggi,
        "batas": batas,
        "bolong": bolong,
        "status_key": kunci,
        "status_label": label,
        "ringkasan_kurang": ringkasan,
    }
