import logging
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.auth import auth_aktif, gerbang_auth, pakai_https
from app.db import init_db
from app.routes import auth as auth_routes
from app.routes import daftar_kurang, export, manga, volume
from app.templating import render

BASE_DIR = Path(__file__).resolve().parent.parent
log = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    if not auth_aktif():
        log.warning(
            "MANGA_PASSWORD kosong: gerbang kata sandi nonaktif. "
            "Jangan host publik tanpa mengisi variabel ini."
        )
    yield


app = FastAPI(title="MangaShelf", docs_url=None, redoc_url=None, lifespan=lifespan)


@app.middleware("http")
async def siapkan_csrf(request: Request, call_next):
    token = request.cookies.get("mangashelf_csrf") or secrets.token_urlsafe(24)
    request.state.csrf = token

    response = await call_next(request)
    if "mangashelf_csrf" not in request.cookies:
        response.set_cookie(
            "mangashelf_csrf",
            token,
            httponly=True,
            samesite="lax",
            secure=pakai_https(request),
        )
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    return response


@app.middleware("http")
async def gerbang_kata_sandi(request: Request, call_next):
    return await gerbang_auth(request, call_next)


app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
app.include_router(auth_routes.router)
app.include_router(manga.router)
app.include_router(volume.router)
app.include_router(daftar_kurang.router)
app.include_router(export.router)


@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}


@app.exception_handler(404)
async def tidak_ditemukan(request: Request, exc):
    response = render(
        request,
        "404.html",
        pesan=getattr(exc, "detail", "Halaman tidak ditemukan."),
    )
    response.status_code = 404
    return response


@app.exception_handler(403)
async def akses_ditolak(request: Request, exc):
    response = render(
        request,
        "404.html",
        pesan=getattr(exc, "detail", "Permintaan ditolak."),
    )
    response.status_code = 403
    return response
