"""Gerbang kata sandi single-user.

Aktif otomatis bila env MANGA_PASSWORD diisi. Sesi disimpan sebagai cookie
bertanda tangan (itsdangerous); tidak ada tabel user dan tidak ada database
tambahan.
"""

import hashlib
import hmac
import os
import secrets
import time
from collections import defaultdict, deque
from pathlib import Path
from urllib.parse import quote

from itsdangerous import BadSignature, URLSafeTimedSerializer
from starlette.responses import RedirectResponse, Response

BASE_DIR = Path(__file__).resolve().parent.parent
NAMA_COOKIE = "mangashelf_sesi"
UMUR_SESI = 60 * 60 * 24 * 30  # 30 hari
PERCOBAAN_MAKS = 8
JENDELA_PERCOBAAN = 15 * 60  # detik
JALUR_BEBAS = {"/masuk", "/healthz"}
AWALAN_BEBAS = ("/static/",)

_percobaan: dict[str, deque[float]] = defaultdict(deque)


def kata_sandi() -> str:
    return os.environ.get("MANGA_PASSWORD", "")


def auth_aktif() -> bool:
    return bool(kata_sandi())


def _lokasi_rahasia() -> Path:
    db = Path(os.environ.get("MANGA_DB", BASE_DIR / "data" / "manga.db"))
    return db.parent / ".session_secret"


def _rahasia() -> str:
    dari_env = os.environ.get("MANGA_SECRET", "").strip()
    if dari_env:
        return dari_env

    lokasi = _lokasi_rahasia()
    lokasi.parent.mkdir(parents=True, exist_ok=True)
    if lokasi.exists():
        isi = lokasi.read_text(encoding="utf-8").strip()
        if isi:
            return isi

    nilai = secrets.token_urlsafe(48)
    lokasi.write_text(nilai, encoding="utf-8")
    return nilai


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(_rahasia(), salt="mangashelf-sesi-v1")


def _sidik_sandi() -> str:
    return hashlib.sha256(kata_sandi().encode("utf-8")).hexdigest()[:16]


def pakai_https(request) -> bool:
    return request.url.scheme == "https" or os.environ.get("MANGA_HTTPS") == "1"


def sesi_valid(request) -> bool:
    if not auth_aktif():
        return True

    token = request.cookies.get(NAMA_COOKIE)
    if not token:
        return False

    try:
        data = _serializer().loads(token, max_age=UMUR_SESI)
    except BadSignature:
        return False

    if not isinstance(data, dict):
        return False
    tersimpan = data.get("p") or ""
    return hmac.compare_digest(tersimpan, _sidik_sandi())


def buat_cookie_sesi(request, response: Response) -> None:
    response.set_cookie(
        NAMA_COOKIE,
        _serializer().dumps({"p": _sidik_sandi()}),
        max_age=UMUR_SESI,
        path="/",
        httponly=True,
        samesite="lax",
        secure=pakai_https(request),
    )


def hapus_cookie_sesi(response: Response) -> None:
    response.delete_cookie(NAMA_COOKIE, path="/", httponly=True, samesite="lax")


def _ip(request) -> str:
    return request.client.host if request.client else "tidak-diketahui"


def terlalu_banyak(request) -> bool:
    riwayat = _percobaan[_ip(request)]
    batas = time.monotonic() - JENDELA_PERCOBAAN
    while riwayat and riwayat[0] < batas:
        riwayat.popleft()
    return len(riwayat) >= PERCOBAAN_MAKS


def catat_gagal(request) -> None:
    _percobaan[_ip(request)].append(time.monotonic())


def bersihkan_percobaan(request) -> None:
    _percobaan.pop(_ip(request), None)


def tujuan_aman(nilai: str) -> str:
    """Hanya izinkan path lokal agar tidak menjadi open redirect."""
    if nilai.startswith("/") and not nilai.startswith("//") and "\\" not in nilai:
        return nilai
    return "/"


async def gerbang_auth(request, call_next):
    path = request.url.path
    bebas = path in JALUR_BEBAS or path.startswith(AWALAN_BEBAS)

    if bebas or sesi_valid(request):
        return await call_next(request)

    if request.headers.get("HX-Request"):
        return Response(status_code=401, headers={"HX-Redirect": "/masuk"})

    if request.method == "GET":
        next_url = path
        if request.url.query:
            next_url += "?" + request.url.query
        return RedirectResponse(
            f"/masuk?next={quote(next_url, safe='/')}", status_code=303
        )

    return RedirectResponse("/masuk", status_code=303)
