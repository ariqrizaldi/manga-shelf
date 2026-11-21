from collections import defaultdict
from datetime import datetime, timezone
from math import ceil
from urllib.parse import quote, urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.db import get_session
from app.models import Manga, Volume
from app.rentang import MAKS_VOLUME
from app.security import verifikasi_csrf
from app.services import (
    STATUS_BACA,
    STATUS_RILIS,
    buat_view,
    nomor_halaman,
)
from app.templating import render
from app.utils import normalisasi_judul

router = APIRouter(dependencies=[Depends(verifikasi_csrf)])
PER_HALAMAN = 24
KELENGKAPAN = {
    "semua": "Semua",
    "bolong": "Ada bolong",
    "belum": "Belum sampai akhir",
    "lengkap": "Lengkap / Terbaru",
    "kosong": "Kosong",
}
URUTAN = {
    "abjad": "Abjad A–Z",
    "terbaru": "Terbaru ditambah",
    "kurang": "Paling banyak kurang",
}


def _semua_view(session: Session) -> list[dict]:
    manga_list = session.exec(select(Manga)).all()
    volume_list = session.exec(select(Volume)).all()
    dimiliki: dict[int, set[int]] = defaultdict(set)
    for v in volume_list:
        dimiliki[v.manga_id].add(v.nomor)
    return [buat_view(m, dimiliki[m.id]) for m in manga_list]


def _filter_view(views, q, kelengkapan, status_baca, rating):
    if q:
        q_norm = normalisasi_judul(q)
        views = [
            v
            for v in views
            if q_norm in v["manga"].judul_norm
            or q_norm in normalisasi_judul(v["manga"].author or "")
        ]
    if kelengkapan == "lengkap":
        views = [v for v in views if v["status_key"] in ("lengkap", "terbaru")]
    elif kelengkapan in ("bolong", "belum", "kosong"):
        views = [v for v in views if v["status_key"] == kelengkapan]
    if status_baca in STATUS_BACA:
        views = [v for v in views if v["manga"].status_baca == status_baca]
    if rating in ("1", "2", "3", "4", "5"):
        views = [v for v in views if str(v["manga"].rating or "") == rating]
    return views


def _urutkan(views, urutan):
    if urutan == "terbaru":
        return sorted(
            views,
            key=lambda v: (v["manga"].tanggal_tambah, v["manga"].id or 0),
            reverse=True,
        )
    if urutan == "kurang":
        return sorted(views, key=lambda v: (-v["kurang"], v["manga"].judul_norm))
    return sorted(views, key=lambda v: v["manga"].judul_norm)


def _dashboard(request: Request, session: Session, q, kelengkapan, status_baca, rating, urutan, view, page):
    semua = _semua_view(session)
    statistik = {
        "total_judul": len(semua),
        "volume_dimiliki": sum(v["dimiliki"] for v in semua),
        "volume_kurang": sum(v["kurang"] for v in semua),
        "belum_lengkap": sum(1 for v in semua if v["dimiliki"] > 0 and v["kurang"] > 0),
    }

    hasil = _urutkan(
        _filter_view(semua, q, kelengkapan, status_baca, rating), urutan
    )
    total_halaman = max(1, ceil(len(hasil) / PER_HALAMAN))
    page = min(max(page, 1), total_halaman)
    mulai = (page - 1) * PER_HALAMAN
    halaman_ini = hasil[mulai : mulai + PER_HALAMAN]

    parameter = {
        "q": q,
        "kelengkapan": kelengkapan if kelengkapan != "semua" else "",
        "status_baca": status_baca,
        "rating": rating,
        "urut": urutan if urutan != "abjad" else "",
        "view": view if view != "grid" else "",
    }
    basis_query = urlencode({k: v for k, v in parameter.items() if v})

    konteks = {
        "views": halaman_ini,
        "statistik": statistik,
        "q": q,
        "kelengkapan": kelengkapan,
        "status_baca": status_baca,
        "rating": rating,
        "urutan": urutan,
        "view": view,
        "page": page,
        "total_halaman": total_halaman,
        "total_hasil": len(hasil),
        "nomor_halaman": nomor_halaman(page, total_halaman),
        "basis_query": basis_query,
        "opsi_kelengkapan": KELENGKAPAN,
        "opsi_urutan": URUTAN,
        "opsi_status_baca": STATUS_BACA,
    }

    nama = "partials/_daftar.html" if request.headers.get("HX-Request") else "index.html"
    return render(request, nama, **konteks)


@router.get("/")
def dashboard(
    request: Request,
    q: str = "",
    kelengkapan: str = "semua",
    status_baca: str = "semua",
    rating: str = "semua",
    urut: str = "abjad",
    view: str = "grid",
    page: int = 1,
    session: Session = Depends(get_session),
):
    return _dashboard(request, session, q.strip(), kelengkapan, status_baca, rating, urut, view, page)


@router.get("/judul")
def daftar_judul(
    request: Request,
    q: str = "",
    kelengkapan: str = "semua",
    status_baca: str = "semua",
    rating: str = "semua",
    urut: str = "abjad",
    view: str = "grid",
    page: int = 1,
    session: Session = Depends(get_session),
):
    return _dashboard(request, session, q.strip(), kelengkapan, status_baca, rating, urut, view, page)


def _ambil_manga(session: Session, manga_id: int) -> Manga:
    manga = session.get(Manga, manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Judul tidak ditemukan.")
    return manga


def _nilai_form(form) -> dict:
    return {
        "judul": (form.get("judul") or "").strip(),
        "author": (form.get("author") or "").strip(),
        "status_rilis": form.get("status_rilis") or "ongoing",
        "total_volume": (form.get("total_volume") or "").strip(),
        "status_baca": form.get("status_baca") or "belum",
        "rating": form.get("rating") or "",
        "catatan": (form.get("catatan") or "").strip(),
        "cover_url": (form.get("cover_url") or "").strip(),
    }


def _validasi(nilai: dict, tertinggi: int = 0) -> tuple[dict, dict]:
    errors: dict[str, str] = {}
    judul = nilai["judul"]
    if not judul:
        errors["judul"] = "Judul wajib diisi."
    elif len(judul) > 200:
        errors["judul"] = "Judul maksimal 200 karakter."

    total = 0
    if nilai["total_volume"]:
        try:
            total = int(nilai["total_volume"])
        except ValueError:
            errors["total_volume"] = "Total volume harus berupa angka."
        else:
            if total < 0 or total > MAKS_VOLUME:
                errors["total_volume"] = f"Total volume harus 0–{MAKS_VOLUME}."
            elif total < tertinggi:
                errors["total_volume"] = (
                    f"Volume {tertinggi} masih dimiliki. Hapus dulu sebelum menurunkan total."
                )

    if nilai["rating"]:
        try:
            rating = int(nilai["rating"])
            if not 1 <= rating <= 5:
                raise ValueError
        except ValueError:
            errors["rating"] = "Rating harus 1–5."

    if nilai["status_rilis"] not in STATUS_RILIS:
        nilai["status_rilis"] = "ongoing"
    if nilai["status_baca"] not in STATUS_BACA:
        nilai["status_baca"] = "belum"

    url = nilai["cover_url"]
    if url and not (url.startswith("http://") or url.startswith("https://")):
        errors["cover_url"] = "URL cover harus diawali http:// atau https://."

    nilai["total_volume"] = str(total)
    return nilai, errors


def _cari_mirip(session: Session, norm: str, kecuali_id=None) -> list[Manga]:
    if not norm:
        return []
    hasil = []
    for m in session.exec(select(Manga)).all():
        if m.id == kecuali_id:
            continue
        if m.judul_norm == norm or (
            len(norm) >= 4 and (norm in m.judul_norm or m.judul_norm in norm)
        ):
            hasil.append(m)
        if len(hasil) >= 3:
            break
    return hasil


def _simpan_dari_form(manga: Manga, nilai: dict) -> None:
    manga.judul = nilai["judul"]
    manga.judul_norm = normalisasi_judul(nilai["judul"])
    manga.author = nilai["author"] or None
    manga.status_rilis = nilai["status_rilis"]
    manga.total_volume = int(nilai["total_volume"] or 0)
    manga.status_baca = nilai["status_baca"]
    manga.rating = int(nilai["rating"]) if nilai["rating"] else None
    manga.catatan = nilai["catatan"] or None
    manga.cover_url = nilai["cover_url"] or None
    manga.tanggal_update = datetime.now(timezone.utc)


@router.get("/manga/baru")
def form_baru(request: Request):
    nilai = {
        "judul": "",
        "author": "",
        "status_rilis": "ongoing",
        "total_volume": "",
        "status_baca": "belum",
        "rating": "",
        "catatan": "",
        "cover_url": "",
    }
    return render(
        request,
        "form.html",
        nilai=nilai,
        errors={},
        mirip=[],
        mode="baru",
        judul_halaman="Tambah manga",
    )


@router.post("/manga/baru")
async def simpan_baru(request: Request, session: Session = Depends(get_session)):
    form = await request.form()
    nilai = _nilai_form(form)
    nilai, errors = _validasi(nilai)
    mirip = []
    if not errors:
        mirip = _cari_mirip(session, normalisasi_judul(nilai["judul"]))
        if mirip and not form.get("konfirmasi"):
            return render(
                request,
                "form.html",
                nilai=nilai,
                errors={},
                mirip=mirip,
                mode="baru",
                judul_halaman="Tambah manga",
            )

    if errors:
        return render(
            request,
            "form.html",
            nilai=nilai,
            errors=errors,
            mirip=[],
            mode="baru",
            judul_halaman="Tambah manga",
        )

    manga = Manga(judul=nilai["judul"])
    _simpan_dari_form(manga, nilai)
    session.add(manga)
    session.commit()
    session.refresh(manga)
    return RedirectResponse(f"/manga/{manga.id}?toast=Tersimpan", status_code=303)


@router.get("/manga/{manga_id}/edit")
def form_edit(request: Request, manga_id: int, session: Session = Depends(get_session)):
    manga = _ambil_manga(session, manga_id)
    nilai = {
        "judul": manga.judul,
        "author": manga.author or "",
        "status_rilis": manga.status_rilis,
        "total_volume": str(manga.total_volume or ""),
        "status_baca": manga.status_baca,
        "rating": str(manga.rating or ""),
        "catatan": manga.catatan or "",
        "cover_url": manga.cover_url or "",
    }
    return render(
        request,
        "form.html",
        nilai=nilai,
        errors={},
        mirip=[],
        mode="edit",
        manga=manga,
        judul_halaman=f"Edit {manga.judul}",
    )


@router.post("/manga/{manga_id}/edit")
async def simpan_edit(
    request: Request,
    manga_id: int,
    session: Session = Depends(get_session),
):
    manga = _ambil_manga(session, manga_id)
    tertinggi = max(
        session.exec(
            select(Volume.nomor).where(Volume.manga_id == manga_id)
        ).all(),
        default=0,
    )
    form = await request.form()
    nilai = _nilai_form(form)
    nilai, errors = _validasi(nilai, tertinggi=tertinggi)
    if errors:
        return render(
            request,
            "form.html",
            nilai=nilai,
            errors=errors,
            mirip=[],
            mode="edit",
            manga=manga,
            judul_halaman=f"Edit {manga.judul}",
        )

    _simpan_dari_form(manga, nilai)
    session.add(manga)
    session.commit()
    return RedirectResponse(f"/manga/{manga.id}?toast=Tersimpan", status_code=303)


@router.post("/manga/{manga_id}/hapus")
def hapus_manga(
    manga_id: int,
    session: Session = Depends(get_session),
):
    manga = _ambil_manga(session, manga_id)
    session.delete(manga)
    session.commit()
    return RedirectResponse(f"/?toast={quote('Judul dihapus')}", status_code=303)


@router.get("/manga/{manga_id}")
def detail_manga(
    request: Request,
    manga_id: int,
    session: Session = Depends(get_session),
):
    manga = _ambil_manga(session, manga_id)
    nomor = set(
        session.exec(select(Volume.nomor).where(Volume.manga_id == manga_id)).all()
    )
    view = buat_view(manga, nomor)
    return render(request, "detail.html", v=view, manga=manga)
