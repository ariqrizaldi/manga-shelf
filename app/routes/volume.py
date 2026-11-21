import json

from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy import delete
from sqlmodel import Session, select

from app.db import get_session
from app.models import Manga, Volume
from app.rentang import MAKS_VOLUME, RentangError, parse_rentang
from app.routes.manga import _ambil_manga
from app.security import verifikasi_csrf
from app.services import buat_view
from app.templating import render

router = APIRouter(dependencies=[Depends(verifikasi_csrf)])


def _nomor_dimiliki(session: Session, manga_id: int) -> set[int]:
    return set(
        session.exec(select(Volume.nomor).where(Volume.manga_id == manga_id)).all()
    )


def _panel(
    request: Request,
    session: Session,
    manga: Manga,
    *,
    error: str | None = None,
    error_area: str = "umum",
    rentang_value: str = "",
    toast: str | None = None,
):
    view = buat_view(manga, _nomor_dimiliki(session, manga.id))
    response = render(
        request,
        "partials/_volume_panel.html",
        v=view,
        error=error,
        error_area=error_area,
        rentang_value=rentang_value,
    )
    if toast:
        response.headers["HX-Trigger"] = json.dumps(
            {"showToast": {"text": toast}}
        )
    return response


def _sentuh(manga: Manga) -> None:
    from datetime import datetime, timezone

    manga.tanggal_update = datetime.now(timezone.utc)


@router.post("/manga/{manga_id}/volume/{nomor}/toggle")
def toggle_volume(
    request: Request,
    manga_id: int,
    nomor: int,
    session: Session = Depends(get_session),
):
    manga = _ambil_manga(session, manga_id)
    if nomor < 1 or nomor > MAKS_VOLUME:
        return _panel(request, session, manga, error=f"Nomor {nomor} tidak valid.")
    if manga.total_volume and nomor > manga.total_volume:
        return _panel(
            request,
            session,
            manga,
            error=f"Volume {nomor} melebihi total {manga.total_volume}. Naikkan total dulu.",
        )

    volume = session.get(Volume, (manga_id, nomor))
    if volume:
        session.delete(volume)
    else:
        session.add(Volume(manga_id=manga_id, nomor=nomor))
    _sentuh(manga)
    session.add(manga)
    session.commit()
    return _panel(request, session, manga)


@router.post("/manga/{manga_id}/total")
def ubah_total(
    request: Request,
    manga_id: int,
    delta: int = Form(...),
    session: Session = Depends(get_session),
):
    manga = _ambil_manga(session, manga_id)
    baru = manga.total_volume + delta
    if baru < 0:
        return _panel(
            request,
            session,
            manga,
            error="Total volume tidak bisa negatif.",
            error_area="total",
        )
    if baru > MAKS_VOLUME:
        return _panel(
            request,
            session,
            manga,
            error=f"Total volume maksimal {MAKS_VOLUME}.",
            error_area="total",
        )
    tertinggi = max(_nomor_dimiliki(session, manga_id), default=0)
    if baru < tertinggi:
        return _panel(
            request,
            session,
            manga,
            error=f"Volume {tertinggi} masih dimiliki. Hapus dulu sebelum menurunkan total.",
            error_area="total",
        )

    manga.total_volume = baru
    _sentuh(manga)
    session.add(manga)
    session.commit()
    return _panel(request, session, manga)


@router.post("/manga/{manga_id}/rilis")
def ubah_rilis(
    request: Request,
    manga_id: int,
    value: str = Form(...),
    session: Session = Depends(get_session),
):
    manga = _ambil_manga(session, manga_id)
    if value not in ("ongoing", "tamat"):
        return _panel(
            request,
            session,
            manga,
            error="Status rilis tidak dikenal.",
            error_area="rilis",
        )
    manga.status_rilis = value
    _sentuh(manga)
    session.add(manga)
    session.commit()
    return _panel(request, session, manga)


@router.post("/manga/{manga_id}/volume-baru")
def volume_baru(
    request: Request,
    manga_id: int,
    session: Session = Depends(get_session),
):
    manga = _ambil_manga(session, manga_id)
    if manga.status_rilis != "ongoing":
        return _panel(
            request,
            session,
            manga,
            error="Tombol ini hanya untuk judul Ongoing.",
            error_area="total",
        )
    if manga.total_volume >= MAKS_VOLUME:
        return _panel(
            request,
            session,
            manga,
            error=f"Total volume maksimal {MAKS_VOLUME}.",
            error_area="total",
        )
    manga.total_volume += 1
    _sentuh(manga)
    session.add(manga)
    session.commit()
    return _panel(
        request,
        session,
        manga,
        toast=f"Volume {manga.total_volume} ditambahkan sebagai kekurangan.",
    )


@router.post("/manga/{manga_id}/punya-semua")
def punya_semua(
    request: Request,
    manga_id: int,
    session: Session = Depends(get_session),
):
    manga = _ambil_manga(session, manga_id)
    if manga.total_volume <= 0:
        return _panel(
            request,
            session,
            manga,
            error="Isi total volume dulu untuk menandai semua.",
            error_area="total",
        )
    dimiliki = _nomor_dimiliki(session, manga_id)
    for nomor in range(1, manga.total_volume + 1):
        if nomor not in dimiliki:
            session.add(Volume(manga_id=manga_id, nomor=nomor))
    _sentuh(manga)
    session.add(manga)
    session.commit()
    return _panel(
        request,
        session,
        manga,
        toast=f"Semua volume 1–{manga.total_volume} ditandai dimiliki.",
    )


@router.post("/manga/{manga_id}/kosongkan")
def kosongkan(
    request: Request,
    manga_id: int,
    session: Session = Depends(get_session),
):
    manga = _ambil_manga(session, manga_id)
    session.exec(delete(Volume).where(Volume.manga_id == manga_id))
    _sentuh(manga)
    session.add(manga)
    session.commit()
    return _panel(request, session, manga, toast="Semua catatan volume dikosongkan.")


@router.post("/manga/{manga_id}/rentang")
def terapkan_rentang(
    request: Request,
    manga_id: int,
    rentang: str = Form(""),
    mode: str = Form("tambah"),
    session: Session = Depends(get_session),
):
    manga = _ambil_manga(session, manga_id)
    try:
        angka = parse_rentang(rentang)
    except RentangError as exc:
        return _panel(
            request,
            session,
            manga,
            error=str(exc),
            error_area="rentang",
            rentang_value=rentang,
        )

    if not angka:
        return _panel(
            request,
            session,
            manga,
            error="Isi rentang volume dulu. Contoh: 1-20, 25, 30-44.",
            error_area="rentang",
            rentang_value=rentang,
        )
    if manga.total_volume and max(angka) > manga.total_volume:
        return _panel(
            request,
            session,
            manga,
            error=f"Volume {max(angka)} melebihi total {manga.total_volume}. Naikkan total dulu.",
            error_area="rentang",
            rentang_value=rentang,
        )

    dimiliki = _nomor_dimiliki(session, manga_id)
    if mode == "tambah":
        for nomor in sorted(angka - dimiliki):
            session.add(Volume(manga_id=manga_id, nomor=nomor))
        pesan = "Rentang ditambahkan."
    elif mode == "hapus":
        dihapus = dimiliki & angka
        for nomor in sorted(dihapus):
            session.exec(
                delete(Volume).where(
                    Volume.manga_id == manga_id, Volume.nomor == nomor
                )
            )
        pesan = (
            f"{len(dihapus)} volume dihapus."
            if dihapus
            else "Tidak ada volume yang dihapus."
        )
    elif mode == "ganti":
        session.exec(delete(Volume).where(Volume.manga_id == manga_id))
        for nomor in sorted(angka):
            session.add(Volume(manga_id=manga_id, nomor=nomor))
        pesan = f"Catatan volume diganti ({len(angka)} volume)."
    else:
        return _panel(
            request,
            session,
            manga,
            error="Mode penerapan tidak dikenal.",
            error_area="rentang",
            rentang_value=rentang,
        )

    _sentuh(manga)
    session.add(manga)
    session.commit()
    return _panel(request, session, manga, toast=pesan)


@router.get("/manga/{manga_id}/rentang/preview")
def preview_rentang(
    request: Request,
    manga_id: int,
    rentang: str = "",
    session: Session = Depends(get_session),
):
    manga = _ambil_manga(session, manga_id)
    if not rentang.strip():
        return render(request, "partials/_preview.html", kosong=True)
    try:
        angka = parse_rentang(rentang)
    except RentangError as exc:
        return render(request, "partials/_preview.html", error=str(exc))
    if not angka:
        return render(request, "partials/_preview.html", kosong=True)

    dimiliki = _nomor_dimiliki(session, manga_id)
    tambah = len(angka - dimiliki)
    hapus = len(angka & dimiliki)
    return render(
        request,
        "partials/_preview.html",
        jumlah=len(angka),
        tambah=tambah,
        hapus=hapus,
    )
