import os
import tempfile
from pathlib import Path

os.environ["MANGA_DB"] = str(
    Path(tempfile.mkdtemp(prefix="mangashelf-uji-")) / "manga.db"
)
os.environ["MANGA_SECRET"] = "rahasia-uji-yang-panjang"
os.environ["MANGA_PASSWORD"] = "kata-sandi-uji"

from fastapi.testclient import TestClient  # noqa: E402

from app.auth import tujuan_aman  # noqa: E402
from app.main import app  # noqa: E402


def _csrf(client: TestClient) -> str:
    return client.cookies.get("mangashelf_csrf") or ""


def test_tujuan_aman_menolak_url_luar():
    assert tujuan_aman("/daftar-kurang?x=1") == "/daftar-kurang?x=1"
    assert tujuan_aman("//evil.example") == "/"
    assert tujuan_aman("https://evil.example") == "/"
    assert tujuan_aman("\\\\evil") == "/"


def test_halaman_terlindungi_dialihkan_ke_masuk():
    with TestClient(app) as client:
        respons = client.get("/", follow_redirects=False)
        assert respons.status_code == 303
        assert respons.headers["location"].startswith("/masuk")


def test_login_tanpa_csrf_ditolak():
    with TestClient(app) as client:
        respons = client.post("/masuk", data={"sandi": "kata-sandi-uji"})
        assert respons.status_code == 403


def test_kata_sandi_salah_ditolak():
    with TestClient(app) as client:
        client.get("/masuk")
        respons = client.post(
            "/masuk",
            data={"sandi": "salah", "csrf_token": _csrf(client), "next": "/"},
        )
        assert respons.status_code == 200
        assert "Kata sandi salah" in respons.text
        assert "mangashelf_sesi" not in client.cookies


def test_login_berhasil_lalu_keluar():
    with TestClient(app) as client:
        client.get("/masuk")
        respons = client.post(
            "/masuk",
            data={
                "sandi": "kata-sandi-uji",
                "csrf_token": _csrf(client),
                "next": "/",
            },
            follow_redirects=False,
        )
        assert respons.status_code == 303
        assert respons.headers["location"] == "/"
        assert client.cookies.get("mangashelf_sesi")

        assert client.get("/").status_code == 200

        respons = client.post(
            "/keluar",
            data={"csrf_token": _csrf(client)},
            follow_redirects=False,
        )
        assert respons.status_code == 303
        assert client.get("/", follow_redirects=False).status_code == 303
