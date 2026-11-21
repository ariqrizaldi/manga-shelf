from math import ceil

from app.rentang import hitung_kelengkapan

BADGE_STATUS = {
    "kosong": "badge-kosong",
    "bolong": "badge-bolong",
    "belum": "badge-belum",
    "berurutan": "badge-belum",
    "lengkap": "badge-lengkap",
    "terbaru": "badge-lengkap",
}

STATUS_BACA = {
    "belum": "Belum dibaca",
    "sedang": "Sedang dibaca",
    "selesai": "Selesai",
    "dihentikan": "Dihentikan",
}

STATUS_RILIS = {"ongoing": "Ongoing", "tamat": "Tamat"}

BULAN = [
    "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
    "Jul", "Agu", "Sep", "Okt", "Nov", "Des",
]


def buat_segmen(total: int, dimiliki: set[int]) -> list[dict]:
    """Segmen bar progres: satu per volume, dikelompokkan bila lebih dari 64."""
    acuan = total or (max(dimiliki) if dimiliki else 0)
    if acuan <= 0:
        return []
    if acuan <= 64:
        return [{"pct": 100 if n in dimiliki else 0} for n in range(1, acuan + 1)]

    ukuran = ceil(acuan / 64)
    segmen = []
    for mulai in range(1, acuan + 1, ukuran):
        akhir = min(mulai + ukuran - 1, acuan)
        jumlah = sum(1 for n in range(mulai, akhir + 1) if n in dimiliki)
        segmen.append({"pct": round(jumlah / (akhir - mulai + 1) * 100)})
    return segmen


def buat_view(manga, nomor_dimiliki) -> dict:
    dimiliki = set(nomor_dimiliki)
    k = hitung_kelengkapan(manga.total_volume, dimiliki, manga.status_rilis)
    return {
        "manga": manga,
        "dimiliki_set": dimiliki,
        **k,
        "badge": BADGE_STATUS.get(k["status_key"], "badge-kosong"),
        "segments": buat_segmen(manga.total_volume, dimiliki),
        "status_baca_label": STATUS_BACA.get(manga.status_baca, "Belum dibaca"),
        "status_rilis_label": STATUS_RILIS.get(manga.status_rilis, "Ongoing"),
        "tanggal_label": format_tanggal(manga.tanggal_tambah),
    }


def format_tanggal(nilai) -> str:
    if not nilai:
        return ""
    return f"{nilai.day} {BULAN[nilai.month - 1]} {nilai.year}"


def nomor_halaman(sekarang: int, total: int) -> list:
    """Daftar nomor halaman dengan -1 sebagai penanda elipsis."""
    if total <= 7:
        return list(range(1, total + 1))
    halaman = {1, total, sekarang - 1, sekarang, sekarang + 1}
    if sekarang <= 3:
        halaman.update({2, 3, 4})
    if sekarang >= total - 2:
        halaman.update({total - 1, total - 2, total - 3})
    urut = sorted(n for n in halaman if 1 <= n <= total)
    hasil = []
    for n in urut:
        if hasil and n - hasil[-1] > 1:
            hasil.append(-1)
        hasil.append(n)
    return hasil
