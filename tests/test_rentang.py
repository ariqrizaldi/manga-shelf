import pytest

from app.rentang import (
    RentangError,
    hitung_kelengkapan,
    kompres_rentang,
    parse_rentang,
)


def test_parse_rentang_campuran():
    assert parse_rentang("1-20, 25, 30-44") == set(range(1, 21)) | {25} | set(range(30, 45))


def test_parse_spasi_dan_tumpang_tindih():
    assert parse_rentang(" 1-10  5-15 ") == set(range(1, 16))


@pytest.mark.parametrize("teks", ["44-30", "0", "1001", "abc", "1-1001"])
def test_parse_rentang_tidak_valid(teks):
    with pytest.raises(RentangError):
        parse_rentang(teks)


def test_kompres_rentang():
    assert kompres_rentang([21, 22, 23, 24, 31, 32, 40]) == "21-24, 31-32, 40"
    assert kompres_rentang([]) == ""


def test_kelengkapan_contoh_naruto():
    dimiliki = parse_rentang("1-24, 30-42, 55-72")
    hasil = hitung_kelengkapan(72, dimiliki, "tamat")
    assert hasil["dimiliki"] == 55
    assert hasil["kurang"] == 17
    assert hasil["status_key"] == "bolong"
    assert hasil["ringkasan_kurang"] == "Belum punya: 25-29, 43-54"


def test_kelengkapan_ongoing_terbaru_dan_baru_terbit():
    penuh = hitung_kelengkapan(112, set(range(1, 113)), "ongoing")
    assert penuh["status_key"] == "terbaru"
    assert penuh["kurang"] == 0

    kurang_satu = hitung_kelengkapan(113, set(range(1, 113)), "ongoing")
    assert kurang_satu["status_key"] == "belum"
    assert kurang_satu["ringkasan_kurang"] == "Belum punya: 113"


def test_kelengkapan_tanpa_total_dan_kosong():
    tanpa_total = hitung_kelengkapan(0, {1, 2, 3, 4}, "ongoing")
    assert tanpa_total["status_key"] == "berurutan"
    assert tanpa_total["kurang"] == 0

    kosong = hitung_kelengkapan(10, set(), "tamat")
    assert kosong["status_key"] == "kosong"
    assert kosong["kurang"] == 10
